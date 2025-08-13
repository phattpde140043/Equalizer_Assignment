# Models/RealtimeRecorder.py
import sounddevice as sd
import numpy as np
import queue
import threading
import time

class RealtimeRecorder:
    def __init__(self, samplerate=16000, channels=1, blocksize=1024, dtype='float32',
                 on_chunk=None, on_state=None, device=None,
                 batch_ms=240, max_wait_ms=350):
        self.sr = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.dtype = dtype
        self.on_chunk = on_chunk
        self.on_state = on_state
        self.device = device
        self.batch_ms = batch_ms
        self.max_wait_ms = max_wait_ms

        self._q = queue.Queue()
        self._stream = None
        self._collector = None
        self._stop = threading.Event()
        self._is_recording = False

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        data = np.copy(indata[:, 0] if self.channels == 1 else indata).astype(np.float32)
        self._q.put(data)

    def _collector_loop(self):
        if self.on_state:
            self.on_state(True)

        target_frames = int(self.sr * self.batch_ms / 1000.0)
        force_flush_after = self.max_wait_ms / 1000.0

        buf, buf_len = [], 0
        last_flush = time.time()

        def flush():
            nonlocal buf, buf_len, last_flush
            if buf_len == 0:
                return
            chunk = np.concatenate(buf, axis=0) if len(buf) > 1 else buf[0]
            if self.on_chunk:
                self.on_chunk(chunk, self.sr)
            buf, buf_len = [], 0
            last_flush = time.time()

        while not self._stop.is_set():
            timeout = max(0.0, force_flush_after - (time.time() - last_flush))
            try:
                part = self._q.get(timeout=timeout)
                buf.append(part); buf_len += part.shape[0]
                if buf_len >= target_frames:
                    flush()
            except queue.Empty:
                flush()

        flush()
        if self.on_state:
            self.on_state(False)

    def start(self):
        if self._is_recording:
            return
        self._stop.clear()
        self._stream = sd.InputStream(
            samplerate=self.sr,
            channels=self.channels,
            blocksize=self.blocksize,
            dtype=self.dtype,
            callback=self._audio_callback,
            device=self.device
        )
        self._stream.start()
        self._collector = threading.Thread(target=self._collector_loop, daemon=True)
        self._collector.start()
        self._is_recording = True

    def stop(self):
        if not self._is_recording:
            return
        self._stop.set()
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
        finally:
            self._stream = None
        if self._collector and self._collector.is_alive():
            self._collector.join(timeout=1.0)
        self._is_recording = False

    @property
    def is_recording(self):
        return self._is_recording
