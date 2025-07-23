import os
from yt_dlp import YoutubeDL

# Create output directory if it doesn't exist
output_dir = './outputs'
os.makedirs(output_dir, exist_ok=True)

vids = ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    # Output template - downloads to ./outputs/ directory
    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    'ignoreerrors': True,  # Continue on download errors
}

try:
    with YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading {len(vids)} video(s)...")
        ydl.download(vids)
        print("Download completed!")
except Exception as e:
    print(f"Error during download: {e}")