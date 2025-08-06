import tkinter as tk
from tkinter import filedialog
from AudioPlayer import AudioPlayer
import Controller.Main_controller as control
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import common.utils as util
import numpy as np

# Tạo Cửa sổ chính
root = tk.Tk()
root.title("Giao diện chính")
root.geometry("1200x900")       # Kích thước ban đầu
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

# Hàm vẽ mẫu spectrogram (placeholder)
def plot_spectrogram(ax, sr=44100):
    ax.clear()
    # tạo dữ liệu giả cho spectrogram
    S = np.abs(np.random.randn(256, 256))
    im = ax.imshow(20*np.log10(S + 1e-6), origin='lower', aspect='auto')
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

def make_chart_block(parent):
    block = {}
    # waveform (top)
    wf_frame = tk.Frame(parent)
    wf_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    fig_wf, ax_wf, canvas_wf, widget_wf = create_matplotlib_canvas(wf_frame, height=1.6)
    widget_wf.pack(fill=tk.BOTH, expand=True)
    control.plot_waveform(ax_wf,player=player)
    canvas_wf.draw()

    # spectrogram (middle)
    spec_frame = tk.Frame(parent, height=150)
    spec_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=6)
    fig_spec, ax_spec, canvas_spec, widget_spec = create_matplotlib_canvas(spec_frame, height=1.2)
    widget_spec.pack(fill=tk.BOTH, expand=True)
    plot_spectrogram(ax_spec)
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
    prev_btn = tk.Button(btns, text="⏮", width=3)
    prev_btn.pack(side=tk.LEFT, padx=2)
    play_btn = tk.Button(btns, text="▶", width=3, command=lambda: control.handle_play(player))
    play_btn.pack(side=tk.LEFT, padx=2)
    pause_btn = tk.Button(btns, text="⏸", width=3, command=lambda: control.handle_pause(player))
    pause_btn.pack(side=tk.LEFT, padx=2)
    stop_btn = tk.Button(btns, text="⏹", width=3, command=lambda: control.handle_stop(player))
    stop_btn.pack(side=tk.LEFT, padx=2)
    next_btn = tk.Button(btns, text="⏭", width=3)
    next_btn.pack(side=tk.LEFT, padx=2)

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

    block['seek'] = seek                # Thanh seek thời gian
    block['time_left'] = time_left      # Nhãn thời gian bên trái (ví dụ: "0:00")
    block['time_right'] = time_right    # Nhãn thời gian bên phải (ví dụ: "1:45")
    block['waveform_hash'] = None
    return block

left_block = make_chart_block(left_chart_container)
right_block = make_chart_block(right_chart_container)

# Equalizer frame (8 thanh)
band_frame = tk.Frame(equalizer_frame)
band_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

freqs = ["2.2K","4.4K","6.6K","8.8K","11K","13.2K","15.4K","17.6K"]  # ví dụ
scales = []

for i, f in enumerate(freqs):
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
    freq_label = tk.Label(col, text=f)
    freq_label.pack(side=tk.TOP, pady=(2,0))
    s.config(command= lambda: control.make_callback(db_label))

    scales.append(s)


# Footer chứa nút thoát
footer = tk.Frame(root)
footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

btn_quit = tk.Button(footer, text="Đóng ứng dụng",command=lambda: control.handle_quit(root) )
btn_quit.pack()

def periodic_update():
    control.update_seek_bar(player, left_block)
    control.update_seek_bar(player, right_block)

    # === Cập nhật waveform nếu audio_data mới ==
    if player.get_Data() is not None:
        current_id = util.hash_audio_data(player.get_Data())
        if left_block.get('waveform_hash') != current_id:
            control.plot_waveform(left_block.get('ax_wf'),player)
            left_block['waveform_hash'] = current_id
            left_block.get('canvas_wf').draw()
        
    
    # Gọi lại chính nó sau 100ms
    root.after(100, periodic_update)

# Bắt đầu vòng lặp
periodic_update()

root.mainloop()

