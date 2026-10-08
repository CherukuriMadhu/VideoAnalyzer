import cv2


def extract_frames(video_path, max_frames=5, threshold=30):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Could not open video")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if total_frames == 0 or fps == 0:
        cap.release()
        raise ValueError("Invalid video")

    representative_indices = [
        int(i * (total_frames - 1) / (max_frames - 1))
        for i in range(max_frames)
    ]

    frames = []

    for index in representative_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        success, frame = cap.read()

        if success:
            timestamp = index / fps
            frames.append((frame.copy(), timestamp))

    cap.release()

    return frames