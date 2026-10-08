import re
import subprocess
from difflib import SequenceMatcher
from functools import lru_cache

import whisper


# =========================================================
# WHISPER MODEL
# =========================================================

@lru_cache(maxsize=1)
def load_whisper_model(model_name="tiny.en"):
    """
    Load Whisper once and reuse it for future videos.
    """

    return whisper.load_model(model_name)


# =========================================================
# AUDIO EXTRACTION
# =========================================================

def extract_audio(video_path, audio_path="audio.wav"):

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Could not extract audio from video.\n"
            + result.stderr
        )

    return audio_path


# =========================================================
# DETECT REPETITIVE / HALLUCINATED SEGMENTS
# =========================================================

def is_repetitive_segment(text):
    """
    Detect obvious Whisper hallucinations such as:

    Oh, oh, oh, oh, oh, oh, oh...

    We remove highly repetitive short segments while
    keeping normal sentences.
    """

    words = re.findall(
        r"\b[a-zA-Z']+\b",
        text.lower()
    )

    if len(words) < 6:
        return False

    word_counts = {}

    for word in words:

        word_counts[word] = (
            word_counts.get(word, 0) + 1
        )

    most_common_count = max(
        word_counts.values()
    )

    repetition_ratio = (
        most_common_count / len(words)
    )

    # Example:
    # oh oh oh oh oh oh
    # -> ratio = 1.0
    #
    # Normal sentence:
    # I'm going to take a look at the one
    # -> much lower ratio

    if (
        len(word_counts) <= 2
        and repetition_ratio >= 0.75
    ):
        return True

    return False


# =========================================================
# REMOVE DUPLICATE SEGMENTS
# =========================================================

def remove_duplicate_segments(segments):

    cleaned_segments = []

    for segment in segments:

        text = segment["text"].strip()

        if not text:
            continue


        # -------------------------------------------------
        # Remove obvious repetitive hallucinations
        # -------------------------------------------------

        if is_repetitive_segment(text):
            continue


        current_start = segment["start"]

        is_duplicate = False


        # -------------------------------------------------
        # Compare with previous segments
        # -------------------------------------------------

        for previous in cleaned_segments:

            previous_text = previous["text"].strip()

            previous_start = previous["start"]

            time_difference = (
                current_start - previous_start
            )

            similarity = SequenceMatcher(
                None,
                previous_text.lower(),
                text.lower()
            ).ratio()


            # Ignore repeated text within 60 seconds

            if (
                time_difference <= 60
                and similarity >= 0.90
            ):

                is_duplicate = True

                break


        if not is_duplicate:

            cleaned_segments.append(
                segment
            )

    return cleaned_segments


# =========================================================
# TRANSCRIBE VIDEO
# =========================================================

def transcribe_video(
    video_path,
    model_name="tiny.en"
):

    # -----------------------------------------------------
    # Extract audio
    # -----------------------------------------------------

    audio_path = extract_audio(
        video_path
    )


    # -----------------------------------------------------
    # Load cached Whisper model
    # -----------------------------------------------------

    model = load_whisper_model(
        model_name
    )


    # -----------------------------------------------------
    # Transcribe
    # -----------------------------------------------------

    result = model.transcribe(

        audio_path,

        fp16=False,

        language="en",

        temperature=0,

        condition_on_previous_text=False,

        no_speech_threshold=0.6
    )


    # -----------------------------------------------------
    # Clean transcript
    # -----------------------------------------------------

    cleaned_segments = remove_duplicate_segments(
        result["segments"]
    )


    # -----------------------------------------------------
    # Combine transcript
    # -----------------------------------------------------

    cleaned_text = " ".join(

        segment["text"].strip()

        for segment in cleaned_segments
    )


    return {
        "text": cleaned_text,

        "segments": cleaned_segments
    }