import os
from pydub import AudioSegment


def extract_audio(video_file_path, audio_file_path):
    """
    Extract audio from a video file and save as MP3.
    """
    # Normalize paths
    video_file_path = os.path.abspath(video_file_path)
    audio_file_path = os.path.abspath(audio_file_path)

    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Video file not found: {video_file_path}")

    # Extract audio using pydub
    audio = AudioSegment.from_file(video_file_path)
    audio.export(audio_file_path, format="mp3")
    print(f"Audio extracted: {audio_file_path}")


def split_audio_into_chunks(audio_file_path, audio_chunk_dir, chunk_size=5 * 60 * 1000):
    """
    Split an audio file into smaller chunks and save them.
    """
    # Normalize paths
    audio_file_path = os.path.abspath(audio_file_path)
    audio_chunk_dir = os.path.abspath(audio_chunk_dir)

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Ensure chunk directory exists
    os.makedirs(audio_chunk_dir, exist_ok=True)

    # Split audio into chunks
    print(f"Splitting audio file: {audio_file_path} into chunks at: {audio_chunk_dir}")
    audio = AudioSegment.from_mp3(audio_file_path)
    chunks = list(audio[::chunk_size])

    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(audio_chunk_dir, f"chunk_{i}.mp3")
        chunk.export(chunk_path, format="mp3")
        print(f"Exported chunk: {chunk_path}")


def extract_frames(video_path, frames_dir):
    """
    Extract frames from a video file and save them as images.
    """
    import cv2

    # Normalize paths
    video_path = os.path.abspath(video_path)
    frames_dir = os.path.abspath(frames_dir)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Ensure frames directory exists
    os.makedirs(frames_dir, exist_ok=True)

    # Extract frames
    video = cv2.VideoCapture(video_path)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    success, frame = video.read()
    count, second = 0, 0

    while success:
        if count % fps == 0:  # Save one frame per second
            frame_path = os.path.join(frames_dir, f"frame_{second:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            print(f"Exported frame: {frame_path}")
            second += 1
        success, frame = video.read()
        count += 1

    video.release()
    print(f"Frames extracted to: {frames_dir}")
