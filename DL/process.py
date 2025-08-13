import numpy as np
import joblib
import librosa
import os

def extract_all_features(file_path, label="unknown", sr=22050, segment_duration=3):
    """
    Trích xuất toàn bộ feature từ file audio theo cấu trúc features_3_sec.csv
    
    Parameters:
        file_path (str): Đường dẫn file audio
        label (str): Nhãn (thể loại hoặc tên)
        sr (int): Sampling rate
        segment_duration (float): Thời lượng mỗi đoạn tính feature (giây)
        
    Returns:
        features_list (list): Danh sách các dòng feature
    """
    # Load file
    y, sr = librosa.load(file_path, sr=sr)
    total_duration = librosa.get_duration(y=y, sr=sr)
    
    features_list = []
    num_segments = int(total_duration // segment_duration)
    
    for i in range(num_segments):
        start_sample = int(i * segment_duration * sr)
        end_sample = int(start_sample + segment_duration * sr)
        segment = y[start_sample:end_sample]
        
        if len(segment) < segment_duration * sr:
            continue
        
        # Spectral & chroma
        chroma_stft = librosa.feature.chroma_stft(y=segment, sr=sr)
        rms = librosa.feature.rms(y=segment)
        spec_cent = librosa.feature.spectral_centroid(y=segment, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=segment, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=segment, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(segment)
        
        # Harmonic & percussive
        harmony, perceptr = librosa.effects.hpss(segment)
        
        # Tempo
        tempo = librosa.beat.tempo(y=segment, sr=sr)[0]
        
        # MFCC
        mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=20)
        
        # Build row
        row = [
            os.path.basename(file_path),  # filename
            total_duration,               # length
            np.mean(chroma_stft), np.var(chroma_stft),
            np.mean(rms), np.var(rms),
            np.mean(spec_cent), np.var(spec_cent),
            np.mean(spec_bw), np.var(spec_bw),
            np.mean(rolloff), np.var(rolloff),
            np.mean(zcr), np.var(zcr),
            np.mean(harmony), np.var(harmony),
            np.mean(perceptr), np.var(perceptr),
            tempo
        ]
        
        # Thêm MFCC mean/var
        for m in mfcc:
            row.append(np.mean(m))
            row.append(np.var(m))
        
        # Label
        row.append(label)
        
        features_list.append(row)
    
    return features_list


# Đọc file audio data
audio_path = "path/to/audio" # Đây là đường dẫn tới file audio

features = extract_all_features(audio_path)

min_max_scaler = joblib.load("min_max_scaler.save")
standard_scaler = joblib.load("standard_scaler.save")

features = [row[1:-1] for row in features]
features_scaled = min_max_scaler.transform(features)

features_scaled = [row[1:] for row in features_scaled]
features_scaled = standard_scaler.transform(features_scaled)