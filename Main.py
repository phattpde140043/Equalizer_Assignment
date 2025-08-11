import tkinter as tk
from tkinter import filedialog
from AudioPlayer import AudioPlayer
import Controller.Main_controller as control
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import common.utils as util
import numpy as np
from common.utils import FREQS as freqs,BAND_NAME as band_names

# Tạo Cửa sổ chính
root = tk.Tk()
root.title("Giao diện chính")
root.geometry("1200x1000")       # Kích thước ban đầu
root.minsize(400, 300)         # Kích thước tối thiểu: không thể nhỏ hơn

# === Tạo đối tượng AudioPlayer ===
player = AudioPlayer()


# === Frame chứa các nút điều khiển ===
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

btn_show = tk.Button(control_frame, text="Bắt đầu ghi âm")
btn_show.pack(side=tk.LEFT, padx=10)

btn_upload = tk.Button(control_frame, text="Upload file audio", command = lambda: control.handle_upload(player,root))
btn_upload.pack(side=tk.LEFT, padx=10)

btn_quit = tk.Button(control_frame, text="Đóng ứng dụng",command=lambda: control.handle_quit(root) )
btn_quit.pack(side=tk.RIGHT, padx=10)

# --- Main frame chính giữa control_frame và footer ---
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

# chia main_frame thành 2 phần dọc: chart_frame (top) và equalizer_frame (bottom)
chart_frame = tk.Frame(main_frame)
chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

equalizer_frame = tk.Frame(main_frame, relief=tk.GROOVE, bd=1)
equalizer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8,0))

# Chart frame chia trái - phải
left_chart_container = tk.Frame(chart_frame)
left_chart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,4))

right_chart_container = tk.Frame(chart_frame)
right_chart_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4,0))

# Hàm tiện ích để tạo matplotlib canvas với một axes
def create_matplotlib_canvas(parent, height=2.5):
    fig = Figure(figsize=(6, height), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=parent)
    widget = canvas.get_tk_widget()
    return fig, ax, canvas, widget



def make_chart_block(parent):
    block = {}
    # waveform (top)
    wf_frame = tk.Frame(parent)
    wf_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    fig_wf, ax_wf, canvas_wf, widget_wf = create_matplotlib_canvas(wf_frame, height=1.2)
    widget_wf.pack(fill=tk.BOTH, expand=True)
    control.plot_waveform(ax_wf,player=player)
    canvas_wf.draw()

    # spectrogram (middle)
    spec_frame = tk.Frame(parent)
    spec_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=6)
    fig_spec, ax_spec, canvas_spec, widget_spec = create_matplotlib_canvas(spec_frame, height=1.6)
    widget_spec.pack(fill=tk.BOTH, expand=True)
    control.plot_spectrogram(ax_spec,player)
    canvas_spec.draw()

    # player frame (bottom)
    player_frame = tk.Frame(parent)
    player_frame.pack(side=tk.TOP, fill=tk.X, pady=(6,0))

    # Time labels + slider
    time_left = tk.Label(player_frame, text="0:00")
    time_left.pack(side=tk.LEFT, padx=4)
    seek = ttk.Scale(player_frame, from_=0, to=100, orient=tk.HORIZONTAL)
    seek.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    time_right = tk.Label(player_frame, text="0:00")
    time_right.pack(side=tk.LEFT, padx=4)

    # Playback buttons
    btns = tk.Frame(parent)
    btns.pack(side=tk.TOP, pady=4)

    play_btn = tk.Button(btns, text="▶", width=3)
    play_btn.pack(side=tk.LEFT, padx=2)
    pause_btn = tk.Button(btns, text="⏸", width=3)
    pause_btn.pack(side=tk.LEFT, padx=2)
    stop_btn = tk.Button(btns, text="⏹", width=3)
    stop_btn.pack(side=tk.LEFT, padx=2)
  
    # speed combobox
    speed_label = tk.Label(btns, text="x")
    speed_label.pack(side=tk.LEFT, padx=(10,0))
    speed_combo = ttk.Combobox(btns, values=["0.5","0.75","1.0","1.25","1.5","2.0"], width=4)
    speed_combo.set("1.0")
    speed_combo.pack(side=tk.LEFT, padx=2)

    # trả về các widget để ta có thể cập nhật sau
    block['fig_wf'] = fig_wf            # Figure của waveform
    block['ax_wf'] = ax_wf              # Axes của waveform (để vẽ lại)
    block['canvas_wf'] = canvas_wf      # Canvas để .draw() lại khi cần

    block['fig_spec'] = fig_spec        # Figure của spectrogram
    block['ax_spec'] = ax_spec          # Axes của spectrogram
    block['canvas_spec'] = canvas_spec  # Canvas của spectrogram

    block['play_btn']= play_btn
    block['pause_btn']= pause_btn
    block['stop_btn']= stop_btn

    block['seek'] = seek                # Thanh seek thời gian
    block['time_left'] = time_left      # Nhãn thời gian bên trái (ví dụ: "0:00")
    block['time_right'] = time_right    # Nhãn thời gian bên phải (ví dụ: "1:45")
    block['waveform_hash'] = None
    block['isSeeking'] = False
    return block

left_block = make_chart_block(left_chart_container)
left_block['seek'].bind("<ButtonRelease-1>", lambda event: control.onSeek(event, left_block, player))
left_block['seek'].bind("<Button-1>", lambda event: control.onSeekStart(event, left_block))
left_block['play_btn'].config(command=lambda: control.handle_play(player))
left_block['pause_btn'].config(command=lambda: control.handle_pause(player))
left_block['stop_btn'].config(command=lambda: control.handle_stop(player))
right_block = make_chart_block(right_chart_container)

# Equalizer frame (8 thanh)
band_frame = tk.Frame(equalizer_frame)
band_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

scales = []

for i, (f,n) in enumerate(zip(freqs,band_names)):
    col = tk.Frame(band_frame)
    col.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=6)

    # scale (vertical)
    s = tk.Scale(col, from_=12, to=-12, length=180, resolution=0.5, orient=tk.VERTICAL)
    s.set(0)
    s.pack(side=tk.TOP)

    # label dB
    db_label = tk.Label(col, text="0 dB")
    db_label.pack(side=tk.TOP, pady=(4,0))

    # freq label
    freq_label = tk.Label(col, text=f"{f} Hz")
    freq_label.pack(side=tk.TOP, pady=(2,0))

    # name label
    name_label = tk.Label(col, text=n)
    name_label.pack(side=tk.TOP, pady=(2,0))


    #s.config(command=control.make_callback(db_label,i,freqs,scales))
    # Gán sự kiện khi nhả chuột
    s.bind("<ButtonRelease-1>", lambda e, freq=f, lbl=db_label: control.on_scale_release(e, freq, lbl,freqs,scales))
    scales.append(s)



def periodic_update():
    control.update_seek_bar(player, left_block)
    #control.update_seek_bar(player, right_block)

    # === Cập nhật waveform nếu audio_data mới ==
    if player.get_Data() is not None:
        current_id = util.hash_audio_data(player.get_Data())
        if left_block.get('waveform_hash') != current_id:
            control.plot_waveform(left_block.get('ax_wf'),player)
            control.plot_spectrogram(left_block['ax_spec'],player)
            left_block['waveform_hash'] = current_id
            left_block.get('canvas_wf').draw()
            left_block.get('canvas_spec').draw()
    
    if player.is_finised :
        player.stop()
        
    
    # Gọi lại chính nó sau 1000ms
    root.after(1000, periodic_update)

# Bắt đầu vòng lặp
periodic_update()

root.mainloop()

