import tkinter as tk
from tkinter import filedialog
from AudioPlayer import AudioPlayer
import Controller.Main_controller as control

# Tạo Cửa sổ chính
root = tk.Tk()
root.title("Giao diện chính")
root.geometry("1200x400")       # Kích thước ban đầu
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


#btn_play = tk.Button(control_frame, text="▶ Play", command= lambda: control.handle_play(player))
#btn_play.pack(side=tk.LEFT, padx=5)

#btn_pause = tk.Button(control_frame, text="⏸ Pause", command=lambda: control.handle_pause(player))
#btn_pause.pack(side=tk.LEFT, padx=5)

#btn_stop = tk.Button(control_frame, text="⏹ Stop", command=lambda: control.handle_stop(player))
#btn_stop.pack(side=tk.LEFT, padx=5)

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

root.mainloop()