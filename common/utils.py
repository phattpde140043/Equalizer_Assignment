import numpy as np
import hashlib
from scipy.signal import butter, sosfilt

FREQS = [31.25,62.5,125,250,500,1000,2000,4000,8000,16000]
BAND_NAME = ["Sub-bass","Bass","Low","Low-mid","Mid","Upper mid","Presence","Brilliance","High","Air"]  



# Hàm chuyển đổi milliseconds thành chuỗi định dạng thời gian
def time_stamp(ms):
    hours, remainder = divmod(ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, _ = divmod(remainder, 1_000)
    return ("%d:%02d:%02d" % (hours, minutes, seconds)) if hours else ("%d:%02d" % (minutes, seconds))

def seconds_to_timestamp(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"

# Hàm tạo file audio trắng
def Generate_white_audio (time, sampling_rate) :
    return np.zeros(time*sampling_rate,dtype= np.float32)

# Tạo hash từ dữ liệu audio (cắt nhỏ nếu cần để nhanh hơn)
def hash_audio_data(audio_data: np.ndarray, max_bytes: int = 1_000_000):
    if audio_data is None:
        return None
    # Chuyển dữ liệu sang bytes (chỉ lấy một phần nếu quá dài)
    bytes_data = audio_data[:max_bytes // audio_data.itemsize].tobytes()
    return hashlib.md5(bytes_data).hexdigest()
  
def hash_list(lst):
    return hashlib.sha256(str(lst).encode()).hexdigest()
  
def apply_equalizer(audio: np.ndarray, gains_db, freqs, sr: int) -> np.ndarray:
    """
    Áp dụng EQ theo 10 band lên một chunk audio (real-time).
    gains_db: list/array độ dài == len(freqs) (dB)
    freqs: danh sách tần số center
    """
    if audio is None or audio.size == 0:
        return np.zeros(0, dtype=np.float32)

    # Bảo vệ: nếu gains thiếu/ dư, chuẩn hóa về đúng độ dài
    if gains_db is None:
        gains_db = np.zeros(len(freqs))
    gains_db = np.asarray(gains_db, dtype=float)
    if gains_db.size != len(freqs):
        tmp = np.zeros(len(freqs), dtype=float)
        n = min(len(freqs), gains_db.size)
        tmp[:n] = gains_db[:n]
        gains_db = tmp

    out = np.zeros_like(audio, dtype=np.float64)
    nyq = sr / 2.0

    # Lọc theo dải: biên ±1/√2 octave quanh f_c
    for f_c, g_db in zip(freqs, gains_db):
        low = f_c / np.sqrt(2)
        high = f_c * np.sqrt(2)
        if high >= nyq:
            high = nyq - 100  # để tránh sát biên quá
        if low <= 20:
            low = 20

        if low >= high:
            continue  # ⚠️ Bỏ qua dải lọc không hợp lệ

        try:
            sos = butter(4, [low, high], btype='band', fs=sr, output='sos')
            band = sosfilt(sos, audio)
            out += band * (10 ** (g_db / 20.0))
        except ValueError as e:
            print(f"[EQ] Bỏ qua band {f_c} Hz: {e}")

    # Normalize tránh clip
    max_val = np.max(np.abs(out)) if out.size else 0
    if max_val > 1e-9 and max_val > 1.0:
        out = out / max_val

    return out.astype(np.float32) 


