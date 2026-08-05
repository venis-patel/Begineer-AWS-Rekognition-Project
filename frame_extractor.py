import os
import subprocess

def extract_frames(video_path, output_dir, fps=1):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # names files in the format frame_0001.jpg, frame_0002.jpg, etc.
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    # Build the FFmpeg command
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={fps}',
        '-qscale:v', '2',
        output_pattern
    ]

    try:
        # Run the command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully extracted frames to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error during extraction: {e.stderr.decode()}")

# Run the extract frames
extract_frames('test_video.mp4', 'extracted_frames', fps=1)