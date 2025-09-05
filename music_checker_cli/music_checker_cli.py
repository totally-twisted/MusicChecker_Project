import librosa
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

# ---------------------- Analysis Functions ----------------------

def load_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    return y, sr

def compute_metrics(y):
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = np.mean(rms)
    rms_var = np.var(rms)
    avg_loudness_db = librosa.amplitude_to_db([rms_mean])[0]
    return avg_loudness_db, rms_mean, rms_var

def evaluate_silence(avg_loudness_db, rms_mean, rms_var, db_threshold=-45, rms_threshold=0.003, var_threshold=0.0005):
    """
    Only delete tracks that are basically silent / whisper-level
    """
    if avg_loudness_db < db_threshold and rms_mean < rms_threshold and rms_var < var_threshold:
        return True
    return False

# ---------------------- File Processing ----------------------

def process_file(file_path, bad_files, quarantine_folder):
    file_name = os.path.basename(file_path)
    try:
        y, sr = load_audio(file_path)
        avg_loudness_db, rms_mean, rms_var = compute_metrics(y)
        if evaluate_silence(avg_loudness_db, rms_mean, rms_var):
            # Move to quarantine
            os.makedirs(quarantine_folder, exist_ok=True)
            dest_path = os.path.join(quarantine_folder, file_name)
            shutil.move(file_path, dest_path)
            bad_files.append(f"{file_name} (Silent, {avg_loudness_db:.1f} dB, RMS {rms_mean:.6f}, Var {rms_var:.6f})")
            print(f"Moved to quarantine: {file_name} ({avg_loudness_db:.1f} dB)")
    except Exception as e:
        print(f"Skipping {file_name} due to error: {e}")
        bad_files.append(f"{file_name} (Error)")

# ---------------------- Main Scan ----------------------

def scan_music_folder(folder_path, max_workers=4):
    audio_extensions = (".mp3", ".wav", ".flac", ".ogg")
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(audio_extensions)]

    bad_files = []
    quarantine_folder = os.path.join(folder_path, "Quarantine_Silent")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file, file_path, bad_files, quarantine_folder) for file_path in files]
        for _ in as_completed(futures):
            pass

    report_path = os.path.join(folder_path, "silent_music_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Deleted / Silent Music Files Report\n")
        f.write("===================================\n")
        for file_name in bad_files:
            f.write(f"{file_name}\n")

    print(f"\nScan complete. Report saved to: {report_path}")
    print(f"All silent files moved to: {quarantine_folder}")

# ---------------------- Run ----------------------

if __name__ == "__main__":
    default_music_folder = os.path.join(os.path.expanduser("~"), "Music")
    print(f"Scanning Music folder and moving silent/whisper-level tracks to quarantine: {default_music_folder}")
    scan_music_folder(default_music_folder, max_workers=8)
