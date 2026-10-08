import sys
from app.pipeline import analyze_video
from app.search import search_video


if len(sys.argv) < 2:
    print("Usage: python cli.py <video_path>")
    sys.exit(1)


video_path = sys.argv[1]

print("\nAnalyzing video...\n")

result = analyze_video(video_path)

query = input("\nAsk a question about the video: ")

answer = search_video(
    query,
    result["visual_descriptions"],
    result["chapters"],
    result["transcript_segments"]
)

print("\n========== AI VIDEO SEARCH ==========")
print(answer)
