import numpy as np
import hashlib

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