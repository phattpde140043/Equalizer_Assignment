# 🎶 Digital Audio Equalizer

Dự án xây dựng một ứng dụng Equalizer xử lý âm thanh số (Digital Audio Equalizer) bằng Python, với khả năng:
- Ghi âm và phát lại âm thanh theo thời gian thực.
- Áp dụng bộ lọc **IIR Butterworth** dạng SOS cho 10 băng tần (10-band Equalizer).
- Tự động nhận diện thể loại nhạc (genre classification) bằng mô hình `.h5`.
- Xuất file âm thanh sau khi xử lý ra định dạng `.wav` hoặc `.mp3`.
- Giao diện người dùng trực quan bằng **Tkinter**.

---
## Cài đặt môi trường

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .              # cài đặt editable mode
```
---
## 🚀 Các chức năng chính
- **Record Realtime**: Ghi âm từ micro, hiển thị waveform trực tiếp.
- **Equalizer**: Điều chỉnh 10 băng tần:
  1. 31 Hz (Sub-bass)  
  2. 62 Hz (Bass)  
  3. 125 Hz (Low-mid)  
  4. 250 Hz (Mid)  
  5. 500 Hz (High-mid)  
  6. 1 kHz  
  7. 2 kHz  
  8. 4 kHz  
  9. 8 kHz  
  10. 16 kHz (Brilliance)
- **Music Genre Detection**: Dựa trên đặc trưng tín hiệu, hệ thống phân loại nhạc thuộc thể loại Blues, Jazz, Rock, Pop, v.v...
- **Export**: Xuất file `.wav` hoặc `.mp3` với các tùy chỉnh equalizer.





