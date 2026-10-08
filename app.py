import re
import streamlit as st

from app.pipeline import analyze_video
from app.search import search_video


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Video Analyzer",
    page_icon="🎥",
    layout="wide"
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_timestamp(seconds):
    """Convert seconds into MM:SS format."""

    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    return f"{minutes:02d}:{seconds:02d}"


def clean_visual_description(text):
    """Clean unwanted formatting from vision model output."""

    if not text:
        return ""

    text = text.replace(
        "Here’s a description of what is clearly visible in the image:",
        ""
    )

    text = text.replace(
        "Here's a description of what is clearly visible in the image:",
        ""
    )

    text = re.sub(
        r"\*\*(Subject|Environment|Color|Action):\*\*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"(Subject|Environment|Color|Action):",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove accidental localhost SVG links
    text = re.sub(
        r"\[?svg\]?\(http://localhost:[^)]+\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone svg text
    text = re.sub(
        r"\bsvg\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text
    )

    return text.strip()


def clean_search_result(text):
    """Clean unwanted SVG/markdown artifacts from search output."""

    if not text:
        return ""

    text = re.sub(
        r"\[?svg\]?\(http://localhost:[^)]+\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bsvg\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# =========================================================
# SESSION STATE
# =========================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "video_start_time" not in st.session_state:
    st.session_state.video_start_time = 0


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🎥 AI Video Analyzer")

    st.caption(
        "Multimodal AI Video Intelligence System"
    )

    st.divider()

    st.subheader("🤖 AI Capabilities")

    st.markdown(
        """
        👁️ **Visual Understanding**

        🎙️ **Speech Transcription**

        📝 **AI Summarization**

        📚 **Automatic Chapters**

        🔎 **Natural-Language Search**

        ⏱️ **Timestamp Navigation**

        📄 **Downloadable Report**
        """
    )

    st.divider()

    st.subheader("🧩 Technologies")

    st.markdown(
        """
        🐍 Python

        👁️ OpenCV

        🎙️ Whisper

        🦙 Ollama

        🧠 Gemma 3

        🎞️ FFmpeg

        🌐 Streamlit
        """
    )

    st.divider()

    st.subheader("🔄 Processing Pipeline")

    st.markdown(
        """
        🎥 Video

        ↓

        🎞️ Frame Extraction

        ↓

        👁️ Vision AI

        ↓

        🎙️ Whisper

        ↓

        🧠 AI Summary

        ↓

        📚 Chapters

        ↓

        🔎 Video Search
        """
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.title("🎥 AI Video Analyzer")

st.caption(
    "Analyze videos, understand visual content, "
    "generate summaries, create chapters, "
    "and search important moments using AI."
)


# =========================================================
# VIDEO UPLOAD
# =========================================================

st.header("📤 Upload Video")

uploaded_video = st.file_uploader(
    "Choose a video file",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv"
    ],
    help="Supported formats: MP4, MOV, AVI and MKV"
)


# =========================================================
# VIDEO DISPLAY
# =========================================================

if uploaded_video:

    st.video(
        uploaded_video,
        start_time=st.session_state.video_start_time
    )

    st.write("")

    if st.button(
        "🚀 Analyze Video",
        type="primary",
        use_container_width=True
    ):

        video_path = "uploaded_video.mp4"

        with open(video_path, "wb") as file:

            file.write(
                uploaded_video.getbuffer()
            )

        progress_text = st.empty()

        def update_progress(message):
            progress_text.info(message)

        try:

            with st.spinner(
                "AI is analyzing your video..."
            ):

                result = analyze_video(
                    video_path,
                    progress_callback=update_progress
                )

            st.session_state.result = result

            progress_text.success(
                "✅ Analysis completed!"
            )

            st.rerun()

        except Exception as error:

            progress_text.error(
                f"❌ Analysis failed: {error}"
            )


# =========================================================
# RESULTS
# =========================================================

if st.session_state.result:

    result = st.session_state.result

    st.divider()

    st.success(
        "✅ Analysis completed — AI insights are ready!"
    )

    # --------------------------------
    # ANALYSIS DASHBOARD
    # --------------------------------

    st.markdown(
        '<div class="section-title">📊 Analysis Dashboard</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🎞️ Scenes",
            len(result["visual_descriptions"])
    )

    with col2:
        st.metric(
            "🎙️ Transcript",
            len(result["transcript_segments"])
    )

    with col3:
        st.metric(
            "📚 Chapters",
            len(result["chapters"])
        )

    with col4:
        st.metric(
            "🔎 Search",
            "AI Powered"
        )



    # =====================================================
    # SUMMARY
    # =====================================================

    st.header("📝 Summary")

    with st.container(border=True):

        st.write(
            result["summary"]
        )


    # =====================================================
    # CHAPTERS
    # =====================================================

    st.header("📚 Chapters")

    st.caption(
        "Select a chapter to jump directly to that moment."
    )

    for index, chapter in enumerate(
        result["chapters"]
    ):

        timestamp = chapter["timestamp"]

        time_text = format_timestamp(
            timestamp
        )

        title = chapter["title"]

        col1, col2 = st.columns(
            [6, 1]
        )

        with col1:

            st.markdown(
                f"**🎬 {time_text} — {title}**"
            )

        with col2:

            if st.button(
                "▶ Jump",
                key=f"chapter_{index}"
            ):

                st.session_state.video_start_time = int(
                    timestamp
                )

                st.rerun()


    # =====================================================
    # TIMESTAMPED TRANSCRIPT
    # =====================================================

    st.header("🎙️ Timestamped Transcript")

    st.caption(
        "Click a timestamp to jump to that point in the video."
    )

    for index, segment in enumerate(
        result["transcript_segments"]
    ):

        text = segment["text"].strip()

        if not text:
            continue

        start = segment["start"]

        time_text = format_timestamp(
            start
        )

        col1, col2 = st.columns(
            [1, 7]
        )

        with col1:

            if st.button(
                f"▶ {time_text}",
                key=f"transcript_{index}"
            ):

                st.session_state.video_start_time = int(
                    start
                )

                st.rerun()

        with col2:

            st.write(text)


    # =====================================================
    # VISUAL ANALYSIS
    # =====================================================

    st.header("👁️ Visual Analysis")

    st.caption(
        "AI-generated understanding of representative video scenes."
    )

    for item in result["visual_descriptions"]:

        timestamp = item["timestamp"]

        description = clean_visual_description(
            item["description"]
        )

        time_text = format_timestamp(
            timestamp
        )

        with st.container(border=True):

            st.subheader(
                f"🎞️ Scene at {time_text}"
            )

            st.write(
                description
            )


    # =====================================================
    # VIDEO SEARCH
    # =====================================================

    st.header("🔎 Search Video")

    st.caption(
        "Ask a natural-language question to find relevant moments."
    )

    query = st.text_input(
        "💬 Your question",
        placeholder="Example: When does the butterfly appear?"
    )

    if query:

        with st.spinner(
            "🔎 Searching the video..."
        ):

            search_result = search_video(
                query,
                result["visual_descriptions"],
                result["chapters"],
                result["transcript_segments"]
            )

        search_result = clean_search_result(
            search_result
        )

        st.subheader(
            "🔍 Search Result"
        )

        with st.container(border=True):

            st.write(
                search_result
            )


        # =================================================
        # SEARCH TIMESTAMPS
        # =================================================

        timestamps = re.findall(
            r"\b(\d{2}):(\d{2})\b",
            search_result
        )

        if timestamps:

            st.subheader(
                "⏱️ Relevant Moments"
            )

            for index, (minutes, seconds) in enumerate(
                timestamps
            ):

                total_seconds = (
                    int(minutes) * 60
                    + int(seconds)
                )

                if st.button(
                    f"▶ Jump to {minutes}:{seconds}",
                    key=f"search_{index}"
                ):

                    st.session_state.video_start_time = (
                        total_seconds
                    )

                    st.rerun()


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.header("📄 Download Report")

    report = []

    report.append(
        "AI VIDEO ANALYSIS REPORT"
    )

    report.append(
        "=" * 60
    )

    report.append("")


    # Summary
    report.append(
        "SUMMARY"
    )

    report.append(
        "-" * 60
    )

    report.append(
        result["summary"]
    )

    report.append("")


    # Chapters
    report.append(
        "CHAPTERS"
    )

    report.append(
        "-" * 60
    )

    for chapter in result["chapters"]:

        time_text = format_timestamp(
            chapter["timestamp"]
        )

        report.append(
            f"{time_text} - {chapter['title']}"
        )

    report.append("")


    # Transcript
    report.append(
        "TIMESTAMPED TRANSCRIPT"
    )

    report.append(
        "-" * 60
    )

    for segment in result["transcript_segments"]:

        text = segment["text"].strip()

        if not text:
            continue

        time_text = format_timestamp(
            segment["start"]
        )

        report.append(
            f"{time_text} - {text}"
        )

    report.append("")


    # Visual analysis
    report.append(
        "VISUAL ANALYSIS"
    )

    report.append(
        "-" * 60
    )

    for item in result["visual_descriptions"]:

        time_text = format_timestamp(
            item["timestamp"]
        )

        description = clean_visual_description(
            item["description"]
        )

        report.append(
            f"{time_text} - {description}"
        )

        report.append("")


    report_text = "\n".join(
        report
    )


    st.download_button(
        "📄 Download Analysis Report",
        data=report_text,
        file_name="video_analysis_report.txt",
        mime="text/plain",
        use_container_width=True
    )


    # =====================================================
    # ANALYZE ANOTHER VIDEO
    # =====================================================

    st.divider()

    if st.button(
        "🔄 Analyze Another Video",
        use_container_width=True
    ):

        st.session_state.result = None

        st.session_state.video_start_time = 0

        st.rerun()