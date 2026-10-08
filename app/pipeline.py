from app.frames import extract_frames
from app.vision import describe_frame
from app.transcribe import transcribe_video
from app.describe import combine_information
from app.llm import generate_summary
from app.chapters import create_chapters


def analyze_video(video_path, progress_callback=None):
    if progress_callback:
        progress_callback("🎞️ Extracting video frames...")
    # Extract representative frames with timestamps
    frames = extract_frames(video_path, max_frames=3)

    visual_descriptions = []

    if progress_callback:
        progress_callback("👁️ Analyzing visual content...")

    for frame, timestamp in frames:
        description = describe_frame(frame)

        visual_descriptions.append({
            "timestamp": timestamp,
            "description": description
        })

    # Transcribe audio
    if progress_callback:
        progress_callback("🎙️ Transcribing audio...")

    transcript = transcribe_video(video_path)
    transcript_text = transcript["text"]

    # Extract descriptions for the LLM
    descriptions_only = [
        item["description"]
        for item in visual_descriptions
    ]

    # Generate AI summary
    if progress_callback:
        progress_callback("🧠 Generating AI summary...")

    summary = generate_summary(
        descriptions_only,
        transcript_text
    )
    # Create video chapters
    if progress_callback:
        progress_callback("📚 Creating video chapters...")

    chapters = create_chapters(visual_descriptions)

    return {
        "visual_descriptions": visual_descriptions,
        "transcript": transcript_text,
        "transcript_segments": transcript["segments"],
        "summary": summary,
        "chapters": chapters
    }