import os
import subprocess

def extract_frames(video_path, output_dir, fps=1):
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={fps}',
        '-qscale:v', '2',
        output_pattern
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully extracted frames to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error during extraction: {e.stderr.decode()}")

# Resolve paths relative to this script's own directory
script_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(script_dir, 'test_video.mp4')
output_dir = os.path.join(script_dir, 'extracted_frames')

# Sanity check before even calling ffmpeg
if not os.path.isfile(video_path):
    raise FileNotFoundError(f"Can't find video at: {video_path}")

extract_frames(video_path, output_dir, fps=1)