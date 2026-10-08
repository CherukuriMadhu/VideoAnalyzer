import re
import requests


OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "gemma3:4b"


def format_timestamp(seconds):
    """Convert seconds into MM:SS format."""

    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    return f"{minutes:02d}:{seconds:02d}"


def keyword_search(query, visual_descriptions, chapters, transcript_segments):
    """
    Quickly find relevant video moments using keywords.
    This avoids calling the LLM for simple searches.
    """

    query_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            query.lower()
        )
    )

    matches = []


    # =====================================================
    # SEARCH VISUAL DESCRIPTIONS
    # =====================================================

    for item in visual_descriptions:

        description = item["description"].strip()

        text_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                description.lower()
            )
        )

        score = len(
            query_words & text_words
        )

        if score > 0:

            matches.append({
                "timestamp": item["timestamp"],
                "text": description,
                "score": score,
                "type": "visual"
            })


    # =====================================================
    # SEARCH CHAPTERS
    # =====================================================

    for chapter in chapters:

        title = chapter["title"].strip()

        text_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                title.lower()
            )
        )

        score = len(
            query_words & text_words
        )

        if score > 0:

            matches.append({
                "timestamp": chapter["timestamp"],
                "text": title,
                "score": score,
                "type": "chapter"
            })


    # =====================================================
    # SEARCH TRANSCRIPT
    # =====================================================

    for segment in transcript_segments:

        text = segment["text"].strip()

        text_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                text.lower()
            )
        )

        score = len(
            query_words & text_words
        )

        if score > 0:

            matches.append({
                "timestamp": segment["start"],
                "text": text,
                "score": score,
                "type": "spoken"
            })


    # =====================================================
    # SORT BY RELEVANCE
    # =====================================================

    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    return matches[:5]


def ai_search(
    query,
    matches
):
    """
    Use Gemma only on the small set of relevant matches.
    """

    context = "\n".join(
        f"{format_timestamp(item['timestamp'])} - {item['text']}"
        for item in matches
    )


    prompt = f"""
You are a video search assistant.

User question:
{query}

Possible relevant moments:

{context}

Choose the most relevant moments.

Rules:
- Use only the information provided.
- Do not invent information.
- Return at most 3 results.
- Keep each result short.
- Return ONLY this format:

01:02 - short explanation

If none answer the question, return:

No relevant moment found.
"""


    response = requests.post(
        f"{OLLAMA_URL}/api/generate",

        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        },

        timeout=60
    )


    response.raise_for_status()


    return response.json()["response"].strip()


def search_video(
    query,
    visual_descriptions,
    chapters,
    transcript_segments
):

    # =====================================================
    # FAST KEYWORD SEARCH
    # =====================================================

    matches = keyword_search(
        query,
        visual_descriptions,
        chapters,
        transcript_segments
    )


    # =====================================================
    # NO MATCH
    # =====================================================

    if not matches:

        return "No relevant moment found."


    # =====================================================
    # USE AI ONLY FOR SMALL CONTEXT
    # =====================================================

    try:

        result = ai_search(
            query,
            matches
        )

        return clean_result(
            result
        )

    except requests.exceptions.ReadTimeout:

        # If Gemma is slow, return the keyword matches
        # instead of failing completely.

        return format_matches(
            matches
        )


def format_matches(matches):

    results = []

    for item in matches[:3]:

        time_text = format_timestamp(
            item["timestamp"]
        )

        results.append(
            f"{time_text} - {item['text']}"
        )

    return "\n".join(
        results
    )


def clean_result(text):

    if not text:
        return "No relevant moment found."


    # Remove accidental SVG artifacts
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


    lines = text.splitlines()

    cleaned = []


    for line in lines:

        line = line.strip()

        if not line:
            continue


        # Remove bullets
        line = re.sub(
            r"^[-*]\s*",
            "",
            line
        )


        # Accept timestamps such as:
        # 01:02 - explanation
        # 1:02 - explanation

        match = re.match(
            r"^(\d{1,2}):(\d{2})\s*[-–—:]\s*(.+)$",
            line
        )


        if match:

            minutes = int(
                match.group(1)
            )

            seconds = int(
                match.group(2)
            )

            explanation = match.group(3).strip()


            if seconds >= 60:
                continue


            cleaned.append(
                f"{minutes:02d}:{seconds:02d} - {explanation}"
            )


    if cleaned:

        return "\n".join(
            cleaned[:3]
        )


    if "no relevant moment" in text.lower():

        return "No relevant moment found."


    return text.strip()