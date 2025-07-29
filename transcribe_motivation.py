import os
import subprocess
from pathlib import Path

# Set paths
video_folder = r"G:\My Drive\Videos For Creating Content"
output_folder = Path(video_folder)

# Transcription model
model_size = "base"

# Loop through all video files
for file in os.listdir(video_folder):
    if file.endswith(".mp4") or file.endswith(".webm"):
        video_path = os.path.join(video_folder, file)
        filename_wo_ext = os.path.splitext(file)[0]
        output_path = os.path.join(output_folder, f"{filename_wo_ext}.txt")

        # Run Whisper transcription
        subprocess.run([
            "whisper", video_path,
            "--model", model_size,
            "--output_format", "txt",
            "--output_dir", str(output_folder)
        ])

        print(f"✅ Transcribed: {file} → {output_path}")

