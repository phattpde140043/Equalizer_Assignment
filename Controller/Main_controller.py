from tkinter import filedialog

from common import utils
from common.utils import FREQS as freqs, hash_audio_data, hash_list
from common.utils import apply_equalizer 
from common.utils import apply_equalizer_fast

import numpy as np
import matplotlib

import math
import scipy.signal as signal
from Models.RealtimeRecorder import RealtimeRecorder
from Models.SystemRecorder import SystemRecorder

import threading
from DL.process import extract_all_features
from DL.predict import model, index_label
import joblib


def handle_upload(player,label):
    filepath = filedialog.askopenfilename(
        title="Chọn file audio",
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac"), ("All files", "*.*")]
    )
    if filepath:
        player.load_file(filepath)
        RunPredictFunction(filepath,view_label=label)

def handle_play(player):
    player.play()

def handle_pause(player):
    player.pause()

def handle_stop(player):
    player.stop()

def handle_quit(root):
    root.destroy()

def handle_export(player):
    player.export_audio_dialog()

# update label mỗi khi thay đổi giá trị của equalizer
def on_scale_release(event, f, lbl, scales, player, output_player):
    v = float(event.widget.get())
    lbl.config(text=f"{v:.1f} dB")

    values = [s.get() for s in scales]

    # 🛡️ Chuẩn hóa độ dài cho chắc (10 band)
    if len(values) != len(freqs):
        tmp = np.zeros(len(freqs))
        n = min(len(values), len(freqs))
        tmp[:n] = values[:n]
        values = tmp.tolist()

    # Cập nhật gain đang dùng cho EQ real-time
    player.equalizer_gain = values

    # (Giữ nguyên) xử lý hậu kỳ để hiển thị panel phải nếu bạn muốn so sánh A/B
    if player.get_Data() is None:
        return
    output_player.audio_data = player.getEqualizerData()




# update label của thời gian
def update_seek_bar(player, block):
    # Lấy thời gian hiện tại
    current_time = player.get_current_time()
    total_duration = player.get_duration()
    
    # Cập nhật thanh seek (giá trị phần trăm)
    if total_duration > 0 and block['isSeeking'] is not True:
        percent = (current_time / total_duration) * 100
        pre_value = block['seek'].get()
        if pre_value != percent:
            #print(percent)
            block['seek'].set(percent)
    
    # Cập nhật nhãn thời gian
    block['time_left'].config(text=utils.seconds_to_timestamp(current_time))
    block['time_right'].config(text=utils.seconds_to_timestamp(total_duration))

# Hàm vẽ mẫu waveform (placeholder)
def plot_waveform(ax, player, sr=44100):
    ax.clear()

    if player.get_Data() is None:
        duration =120
        sampling_rate= 44100
        t = np.linspace(0, duration, duration*sampling_rate,endpoint= False)
        data = utils.Generate_white_audio(duration,sampling_rate)
    
    else:
        data = player.get_Data()
        sr = player.get_Sampling_rate()
        print(len(data)/sr)

    if len(data) < 1024:
        ax.set_title("Spectrogram (đang chờ đủ dữ liệu)")
        ax.figure.canvas.draw_idle()
        return
    
    x = np.linspace(0, len(data)/sr, len(data))
    ax.plot(x, data, color='#ff4040')
    ax.set_ylim(-1, 1)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("Normalized Amplitude")
    ax.grid(False)

def onSeek(event, seek, player):
    value = seek.get('seek').get()
    player.seek_to_percent(value)
    seek['isSeeking']= False

def onSeekStart(event, seek):
    seek['isSeeking']= True

# Hàm vẽ mẫu spectrogram (placeholder)
def plot_spectrogram(ax,player):
    ax.clear()

    if player.get_Data() is None:
        duration =120
        sr= 44100
        data = utils.Generate_white_audio(duration,sr)
    else:
        data = player.get_Data()
        sr = player.get_Sampling_rate()

    # tạo dữ liệu giả cho spectrogram
    # Vẽ spectrogram
    Pxx, freqs, bins, im = ax.specgram(
        data,
        NFFT=1024,        # Số điểm FFT
        Fs=sr,            # Tần số lấy mẫu
        noverlap=512,     # Số điểm chồng lấn giữa các frame
        cmap='inferno'    # Bảng màu
    )

    # Cấu hình hiển thị
    ax.set_xlabel("Thời gian (s)")
    ax.set_ylabel("Tần số (Hz)")
    ax.set_title("Spectrogram")
    ax.set_ylim(0, sr / 2)  # Giới hạn hiển thị tới Nyquist freq

# Hàm helper tạo bộ lọc bandpass dạng sos
def bandpass_sos(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], analog=False, btype='band', output='sos')
    return sos
  
def RunPredictFunction(filepath,view_label,label="unknown", callback=None):
    """Tạo thread để chạy feature extraction"""
    def worker():
        feats = extract_all_features(filepath, label=label)
        min_max_scaler = joblib.load("DL/min_max_scaler.save")
        standard_scaler = joblib.load("DL/standard_scaler.save")
        features = [row[1:-1] for row in feats]
        features_scaled = min_max_scaler.transform(features)

        features_scaled = [row[1:] for row in features_scaled]
        features_scaled = standard_scaler.transform(features_scaled)

        model.load_weights('DL/model.weights.h5')
        pred_proba = model.predict(features_scaled)
        pred_class = np.argmax(pred_proba, axis=1)
        #print(index_label[pred_class[0]])
        view_label.config(text=f"Based on signal analysis, the audio file belongs to the {index_label[pred_class[0]]} genre.")

        if callback:
            callback(feats)  # gửi kết quả về cho View (UI)
    t = threading.Thread(target=worker)
    t.start()


class AppController:
    def __init__(self, player, ui_refs=None):
        self.player = player
        self.ui = ui_refs or {}
        self.player.equalizer_gain = np.zeros(len(freqs), dtype=float)

        # Cấu hình audio
        self.samplerate = 16000
        self.blocksize = 1024
        self.batch_ms = 240
        self.max_seconds = 30

        # Cờ bật/tắt từng nguồn + gain mix
        self.enable_mic = True
        self.enable_sys = True
        self.mix_gain_mic = 1.0
        self.mix_gain_sys = 1.0

        # Bộ đệm tạm cho từng nguồn (đồng bộ trước khi mix)
        self._mic_buf = np.zeros(0, dtype=np.float32)
        self._sys_buf = np.zeros(0, dtype=np.float32)

        # Recorder MIC
        self.recorder = RealtimeRecorder(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,     # block lớn vừa phải → callback ít hơn
            batch_ms=self.batch_ms,       # gom 200–300ms cho ổn định
            max_wait_ms=350,
            on_chunk=self._on_chunk_mic,
            on_state=self._on_state
        )
        self.max_seconds = 300  # giới hạn buffer ~5 phút để tránh phình RAM

        # Recorder SYSTEM (loopback)
        self.system_recorder = SystemRecorder(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            batch_ms=self.batch_ms,
            on_chunk=self._on_chunk_sys,
            on_state=None
        )

    # ==== UI state ====
    def _on_state(self, is_recording: bool):
        if 'status_var' in self.ui and self.ui['status_var'] is not None:
            self.ui['status_var'].set("Đang ghi..." if is_recording else "Đã dừng")
        if 'btn_record' in self.ui and self.ui['btn_record'] is not None:
            self.ui['btn_record'].config(
                text="Dừng ghi" if is_recording else "Bắt đầu ghi âm"
            )

    # ==== Callbacks từ 2 nguồn ====
    def _on_chunk_mic(self, chunk: np.ndarray, sr: int):
        if not self.enable_mic:  # bỏ qua nếu tắt mic
            return
        self._append_buf('mic', chunk)
        self._try_mix_and_push()

    def _on_chunk_sys(self, chunk: np.ndarray, sr: int):
        if not self.enable_sys:  # bỏ qua nếu tắt system
            return
        self._append_buf('sys', chunk)
        self._try_mix_and_push()

    # ==== Buffer helpers ====
    def _append_buf(self, which: str, chunk: np.ndarray):
        # Noise-gate nhẹ cho ổn định: giảm cường độ nếu block quá nhỏ
        if (chunk.astype(np.float32) ** 2).mean() < 1e-5:
            chunk = chunk * 0.2

        if which == 'mic':
            self._mic_buf = np.concatenate([self._mic_buf, chunk.astype(np.float32)], axis=0)
        else:
            self._sys_buf = np.concatenate([self._sys_buf, chunk.astype(np.float32)], axis=0)

    def _try_mix_and_push(self):
        mic_len = len(self._mic_buf)
        sys_len = len(self._sys_buf)

        if self.enable_mic and self.enable_sys:
            # Lấy phần chung để tránh lệch
            n = min(mic_len, sys_len)
            if n <= 0:
                return
            mic_part = self._mic_buf[:n]
            sys_part = self._sys_buf[:n]
            # Cắt bỏ phần đã dùng
            self._mic_buf = self._mic_buf[n:]
            self._sys_buf = self._sys_buf[n:]
            # Mix theo gain
            mixed = self.mix_gain_mic * mic_part + self.mix_gain_sys * sys_part

        elif self.enable_mic and not self.enable_sys:
            if mic_len <= 0:
                return
            n = mic_len
            mixed = self._mic_buf[:n]
            self._mic_buf = self._mic_buf[n:]

        elif self.enable_sys and not self.enable_mic:
            if sys_len <= 0:
                return
            n = sys_len
            mixed = self._sys_buf[:n]
            self._sys_buf = self._sys_buf[n:]

        else:
            # Cả hai đều tắt
            return

        # Giới hạn biên độ
        mixed = np.clip(mixed, -1.0, 1.0)

        # EQ nhanh (IIR) với gain hiện tại trên player
        try:
            gains = getattr(self.player, "equalizer_gain", None)
            if gains is not None and len(gains) == len(freqs):
                mixed = apply_equalizer_fast(mixed, gains, freqs, self.samplerate)
        except Exception as e:
            # Không spam log trong realtime
            print("[EQ fast] lỗi:", e)

        # Đẩy vào player buffer (duy trì max_seconds)
        if self.player.get_Data() is None:
            self.player.set_data(mixed, self.samplerate)
        else:
            self.player.append_data(mixed)
            data = self.player.get_Data()
            max_len = int(self.max_seconds * self.samplerate)
            if data.shape[0] > max_len:
                self.player.set_data(data[-max_len:], self.samplerate)

    # ==== Public API ====
    def toggle_record(self):
        if self.recorder.is_recording or self.system_recorder.is_recording:
            self.recorder.stop()
            self.system_recorder.stop()
        else:
            # reset toàn bộ
            self._mic_buf = np.zeros(0, dtype=np.float32)
            self._sys_buf = np.zeros(0, dtype=np.float32)
            self.player.set_data(np.zeros(0, dtype=np.float32), self.samplerate)
            # bắt đầu 2 luồng
            try:
                if self.enable_mic:
                    self.recorder.start()
            except Exception as e:
                print("[MIC] start lỗi:", e)
            try:
                if self.enable_sys:
                    self.system_recorder.start()
            except Exception as e:
                print("[SYSTEM] start lỗi:", e)

    # Tuỳ chọn: API bật/tắt nguồn & chỉnh gain mix ngay trong lúc chạy
    def set_mic_enabled(self, enabled: bool):
        self.enable_mic = bool(enabled)

    def set_system_enabled(self, enabled: bool):
        self.enable_sys = bool(enabled)

    def set_mix_gains(self, mic_gain=1.0, sys_gain=1.0):
        self.mix_gain_mic = float(mic_gain)
        self.mix_gain_sys = float(sys_gain)
