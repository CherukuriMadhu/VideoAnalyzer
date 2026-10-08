from app.frames import extract_frames


def test_extract_frames_returns_five_frames():
    frames = extract_frames("test_video.mp4", max_frames=5)

    assert len(frames) == 5


def test_extract_frames_has_timestamps():
    frames = extract_frames("test_video.mp4", max_frames=5)

    timestamps = [timestamp for frame, timestamp in frames]

    assert timestamps[0] == 0
    assert timestamps[-1] > timestamps[0]