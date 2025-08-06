import tkinter as tk
from tkinter import filedialog
from audio_player import AudioPlayer

# Tạo Cửa sổ chính
root = tk.Tk()
root.title("Giao diện chính")
root.geometry("1200x400")       # Kích thước ban đầu
root.minsize(400, 300)         # Kích thước tối thiểu: không thể nhỏ hơn

# === Frame chứa các nút điều khiển ===
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

btn_show = tk.Button(control_frame, text="Bắt đầu ghi âm")
btn_show.pack(side=tk.LEFT, padx=10)

btn_upload = tk.Button(control_frame, text="Upload file audio")
btn_upload.pack(side=tk.LEFT, padx=10)

# Footer chứa nút thoát
footer = tk.Frame(root)
footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

btn_quit = tk.Button(footer, text="Đóng ứng dụng")
btn_quit.pack()

root.mainloop()