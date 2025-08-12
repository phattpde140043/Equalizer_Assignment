from tkinter import filedialog

from common import utils
from common.utils import FREQS as freqs

import numpy as np
import matplotlib

import math
import scipy.signal as signal

def handle_upload(player, root):
    filepath = filedialog.askopenfilename(
        title="Chọn file audio",
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac"), ("All files", "*.*")]
    )
    if filepath:
        player.load_file(filepath)

def handle_play(player):
    player.play()

def handle_pause(player):
    player.pause()

def handle_stop(player):
    player.stop()

def handle_quit(root):
    root.destroy()

# update label mỗi khi thay đổi giá trị của equalizer
def on_scale_release(event, f, lbl,scales,player,chart_block):
    v = float(event.widget.get())
    lbl.config(text=f"{v:.1f} dB")

    # Tạo dict tổng hợp giá trị của tất cả các scale
    values = [s.get() for s in scales]
    print(values)  # In dict tổng hợp khi nhả chuột

    if player.get_Data() is None:
        return
    
    player.equalizer_gain= values
    drawOutputChart(chart_block, player)



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

def drawOutputChart(chart_block, player):
    if player.get_Data() is None :
        return 
    
    data = player.getEqualizerData()
    sr = player.get_Sampling_rate()
    x = np.linspace(0, len(data)/sr, len(data))
    ax= chart_block['ax_wf']
    ax.clear()
    ax.plot(x, data, color='#ff4040')
    ax.set_ylim(-1, 1)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("Normalized Amplitude")
    ax.grid(False)

    spec_ax = chart_block['ax_spec']

    Pxx, freqs, bins, im = spec_ax.specgram(
        data,
        NFFT=1024,        # Số điểm FFT
        Fs=sr,            # Tần số lấy mẫu
        noverlap=512,     # Số điểm chồng lấn giữa các frame
        cmap='inferno'    # Bảng màu
    )
    # Cấu hình hiển thị
    spec_ax.set_xlabel("Thời gian (s)")
    spec_ax.set_ylabel("Tần số (Hz)")
    spec_ax.set_title("Spectrogram")
    spec_ax.set_ylim(0, sr / 2)  # Giới hạn hiển thị tới Nyquist freq

    chart_block.get('canvas_wf').draw()
    chart_block.get('canvas_spec').draw()

    

