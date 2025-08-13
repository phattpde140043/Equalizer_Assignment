import sounddevice as sd
import numpy as np
import librosa
import threading
import time
from common.utils import FREQS as freqs
import scipy.signal as signal

class AudioPlayer:
    def __init__(self):
        self.audio_data = None       # Dữ liệu âm thanh
        self.sample_rate = None      # Tần số mẫu
        self.stream = None           # Đối tượng stream từ sounddevice
        self.is_playing = False
        self.is_paused = False
        self.is_finised = False
        self.band_Audio=[]
        self.equalizer_gain=[]
        
        self.position = 0            # Vị trí hiện tại (tính theo mẫu)
        self.lock = threading.Lock() # Dùng để đồng bộ

    def load_file(self, filepath):
        if self.audio_data is not None:
            self.clear()
        self.audio_data, self.sample_rate = librosa.load(filepath, sr=None)
        self.position = 0
        print(f"Đã load: {filepath} - {len(self.audio_data)} samples")
        self.FilterByBand()
        self.equalizer_gain=np.zeros(len(freqs))

    #Thêm set_data và append_data
    def set_data(self, data, sr):
        with self.lock:
            self.audio_data = np.asarray(data, dtype=np.float32)
            self.sample_rate = sr
            self.position = 0
            self.is_finised = False

    def append_data(self, chunk):
        with self.lock:
            if self.audio_data is None:
                self.audio_data = np.asarray(chunk, dtype=np.float32)
            else:
                self.audio_data = np.concatenate(
                    [self.audio_data, np.asarray(chunk, dtype=np.float32)],
                    axis=0
                )
    #####################################

    def get_duration(self):
        if self.audio_data is not None and self.sample_rate:
            return len(self.audio_data) / self.sample_rate
        return 0
    
    def seek_to_percent(self, val):
        with self.lock:
            if self.audio_data is not None:
                total_samples = len(self.audio_data)
                new_position = int((float(val) / 100) * total_samples)
                print(new_position)
                self.position = max(0, min(new_position, total_samples - 1))  # đảm bảo trong khoảng
                print(self.position)

    
    def get_Data(self):
        return self.audio_data 
    
    def get_Sampling_rate(self):
        return self.sample_rate

    def get_current_time(self):
        if self.sample_rate:
            return self.position / self.sample_rate
        return 0


    def callback(self, outdata, frames, time_info, status):
        with self.lock:
            if self.audio_data is None or self.is_paused:
                outdata[:] = np.zeros((frames, 1))
                return

            end = self.position + frames
            print(self.position)
            chunk = self.audio_data[self.position:end]

            if len(chunk) < frames:
                outdata[:len(chunk), 0] = chunk
                outdata[len(chunk):] = 0
                self.position=0
                self.is_finised= True
                raise sd.CallbackStop()
                return
            else:
                outdata[:, 0] = chunk

            self.position += frames

    def play(self):
        if self.audio_data is None:
            print("Chưa có dữ liệu để phát")
            return

        if self.is_playing:
            print("Đang phát rồi")
            return

        self.is_playing = True
        self.is_paused = False
        if self.stream is not None :
            self.stream.close()
            self.stream.stop()
            self.stream = None
            
        try:
            self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.callback,
            blocksize=1024
            )
            self.stream.start()
        except Exception as e:
            print(f"Lỗi khi khởi tạo hoặc start audio stream: {e}")
            self.is_playing = False
            self.stream = None

    def pause(self):
        if not self.is_playing:
            return
        self.is_paused = not self.is_paused
        print("Tạm dừng" if self.is_paused else "Tiếp tục")

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_playing = False
        self.is_paused = False
        self.is_finised= False
        self.position = 0
        print("Dừng phát")

    def get_duration(self):
        if self.audio_data is None or self.sample_rate is None:
            return 0
        return len(self.audio_data) / self.sample_rate

    def get_current_time(self):
        return self.position / self.sample_rate if self.sample_rate else 0
    
    def clear(self):
        self.audio_data = None       
        self.sample_rate = None      
        self.stream = None           
        self.is_playing = False
        self.is_paused = False
        self.position = 0            
        self.lock = threading.Lock() 
        self.band_Audio=[]

    def FilterByBand(self):

        # Xử lý từng band
        for f_c in freqs:

            # Tính biên band ±1/√2 octave quanh f_c
            low = f_c / np.sqrt(2)
            high = f_c * np.sqrt(2)
            if high >= self.sample_rate / 2:
                high = self.sample_rate / 2 - 1
        
            # Tạo filter bandpass
            sos = bandpass_sos(low, high, self.sample_rate)

            # Lọc tín hiệu
            filtered = signal.sosfilt(sos,self.audio_data)

            self.band_Audio.append(filtered)

        


    def getEqualizerData(self):
        output = np.zeros_like(self.audio_data, dtype=np.float64)

        for i, (band, gain) in enumerate(zip(self.band_Audio,self.equalizer_gain)) :
            # Chuyển gain dB sang hệ số tuyến tính
            gain_linear = 10**(gain / 20)
            output+= band* gain_linear

        # Chuẩn hóa output tránh vượt quá biên độ
        max_val = np.max(np.abs(output))
        if max_val > 1:
            output = output / max_val

        return output

# Hàm helper tạo bộ lọc bandpass dạng sos
def bandpass_sos(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], analog=False, btype='band', output='sos')
    return sos

