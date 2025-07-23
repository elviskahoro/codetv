import io
import tempfile
from yt_dlp import YoutubeDL

# Store downloaded audio data in memory
audio_data = {}

def progress_hook(d):
    """Hook to capture download progress and data."""
    if d['status'] == 'finished':
        filename = d['filename']
        title = d.get('info_dict', {}).get('title', 'Unknown')

        # Read the file into memory
        try:
            with open(filename, 'rb') as f:
                audio_data[title] = {
                    'data': f.read(),
                    'filename': filename,
                    'size': len(audio_data[title]['data']) if title in audio_data else 0
                }
            print(f"Loaded '{title}' into memory ({len(audio_data[title]['data'])} bytes)")

            # Optionally remove the file after loading to memory
            # os.remove(filename)

        except Exception as e:
            print(f"Error loading file to memory: {e}")

vids = ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]

# Use a temporary directory for intermediate files
with tempfile.TemporaryDirectory() as temp_dir:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Use temporary directory
        'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        'ignoreerrors': True,
        'progress_hooks': [progress_hook],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Processing {len(vids)} video(s) in memory...")
            ydl.download(vids)

            print(f"\nProcessing completed! Audio data stored in memory:")
            for title, data in audio_data.items():
                print(f"- {title}: {len(data['data'])} bytes")

    except Exception as e:
        print(f"Error during processing: {e}")

# Now you can access the audio data from the audio_data dictionary
# Example: audio_bytes = audio_data['Rick Astley - Never Gonna Give You Up (Official Video)']['data']