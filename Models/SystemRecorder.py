import threading, queue, time
import numpy as np
import soundcard as sc

class SystemRecorder:
    """
    Ghi âm tiếng hệ thống (system/loopback audio) dùng soundcard.
    - Không lưu file.
    - Gọi callback `on_chunk(chunk, sr)` mỗi `batch_ms`.
    """

    def __init__(self,
                 samplerate=16000,
                 channels=1,
                 blocksize=2048,
                 batch_ms=240,
                 on_chunk=None,
                 on_state=None,
                 device_name=None):
        self.sr = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.batch_ms = batch_ms
        self.on_chunk = on_chunk
        self.on_state = on_state
        self.device_name = device_name

        self._stop = threading.Event()
        self._reader = None
        self._collector = None
        self._q = queue.Queue()
        self._is_recording = False
        self._rec_ctx = None
        self._rec = None

    @property
    def is_recording(self):
        return self._is_recording

    def _read_loop(self):
        while not self._stop.is_set():
            try:
                data = self._rec.record(numframes=self.blocksize)
                self._q.put_nowait(data)
            except Exception as e:
                print("[SystemRecorder] read error:", e)

    def _collector_loop(self):
        if self.on_state:
            self.on_state(True)

        target_frames = int(self.sr * self.batch_ms / 1000.0)
        buf, buf_len = [], 0
        last_flush = time.time()
        force_flush_after = max(0.25, self.batch_ms / 1000.0 * 1.8)

        def flush():
            nonlocal buf, buf_len, last_flush
            if buf_len == 0:
                return
            chunk = np.concatenate(buf, axis=0) if len(buf) > 1 else buf[0]
            if self.channels == 1 and chunk.ndim > 1:
                chunk = chunk[:, 0].astype(np.float32)
            else:
                chunk = chunk.astype(np.float32)
            if self.on_chunk:
                try:
                    self.on_chunk(chunk, self.sr)
                except Exception as e:
                    print("[SystemRecorder] on_chunk error:", e)
            buf, buf_len = [], 0
            last_flush = time.time()

        try:
            while not self._stop.is_set():
                timeout = max(0.0, force_flush_after - (time.time() - last_flush))
                try:
                    part = self._q.get(timeout=timeout)
                    buf.append(part)
                    buf_len += part.shape[0]
                    if buf_len >= target_frames:
                        flush()
                except queue.Empty:
                    flush()
        finally:
            flush()
            if self.on_state:
                self.on_state(False)

    def start(self):
        if self._is_recording:
            return

        try:
            mic = sc.get_microphone(
                id=self.device_name or str(sc.default_speaker().name),
                include_loopback=True
            )
        except Exception as e:
            print("[SystemRecorder] Không tìm thấy thiết bị loopback khả dụng.")
            return

        self._rec_ctx = mic.recorder(samplerate=self.sr, channels=self.channels)
        self._rec = self._rec_ctx.__enter__()  # Manual enter để dùng record()

        self._stop.clear()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

        self._collector = threading.Thread(target=self._collector_loop, daemon=True)
        self._collector.start()

        self._is_recording = True

    def stop(self):
        if not self._is_recording:
            return
        self._stop.set()

        if self._reader and self._reader.is_alive():
            self._reader.join(timeout=1.0)
        if self._collector and self._collector.is_alive():
            self._collector.join(timeout=1.0)

        try:
            if self._rec:
                self._rec.close()
        except Exception as e:
            print("[SystemRecorder] Recorder close error:", e)

        self._rec = None
        self._is_recording = False

    @staticmethod
    def list_loopback_candidates():
        return [spk.name for spk in sc.all_speakers()]
