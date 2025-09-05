import librosa
import numpy as np
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor, as_completed

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
            os.makedirs(quarantine_folder, exist_ok=True)
            dest_path = os.path.join(quarantine_folder, file_name)
            shutil.move(file_path, dest_path)
            bad_files.append(f"{file_name} (Silent, {avg_loudness_db:.1f} dB, RMS {rms_mean:.6f}, Var {rms_var:.6f})")
    except Exception as e:
        bad_files.append(f"{file_name} (Error)")

# ---------------------- GUI Functionality ----------------------

def scan_folder_gui(folder_path, progress_var, status_label):
    audio_extensions = (".mp3", ".wav", ".flac", ".ogg")
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(audio_extensions)]

    bad_files = []
    quarantine_folder = os.path.join(folder_path, "Quarantine_Silent")

    progress_var.set(0)
    status_label.config(text="Scanning...")

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_file, file_path, bad_files, quarantine_folder) for file_path in files]
        for i, future in enumerate(as_completed(futures), 1):
            progress_var.set(i / len(files) * 100)
            root.update_idletasks()

    report_path = os.path.join(folder_path, "silent_music_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Deleted / Silent Music Files Report\n")
        f.write("===================================\n")
        for file_name in bad_files:
            f.write(f"{file_name}\n")

    status_label.config(text=f"Scan complete! Report saved to: {report_path}")
    messagebox.showinfo("Done", f"Scan complete!\nReport saved to:\n{report_path}\nQuarantine folder: {quarantine_folder}")

# ---------------------- GUI Setup ----------------------

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

def start_scan():
    folder_path = folder_var.get()
    if not folder_path:
        messagebox.showwarning("No folder", "Please select a folder first!")
        return
    scan_folder_gui(folder_path, progress_var, status_label)

root = tk.Tk()
root.title("Music Checker GUI")
root.geometry("500x200")

folder_var = tk.StringVar()
progress_var = tk.DoubleVar()

tk.Label(root, text="Select Music Folder:").pack(pady=5)
tk.Entry(root, textvariable=folder_var, width=50).pack(pady=5)
tk.Button(root, text="Browse", command=select_folder).pack(pady=5)

tk.Button(root, text="Start Scan", command=start_scan).pack(pady=10)

progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var)
progress_bar.pack(fill="x", padx=20, pady=10)

status_label = tk.Label(root, text="Ready")
status_label.pack(pady=5)

root.mainloop()
