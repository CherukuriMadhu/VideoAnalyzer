import requests


OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "gemma3:4b"


def generate_summary(visual_descriptions, transcript):

    visual_text = "\n".join(
        visual_descriptions
    )

    prompt = f"""
You are an AI video summarization assistant.

Create a short, clear summary of the video using the
visual information and transcript below.

VISUAL INFORMATION:
{visual_text}

TRANSCRIPT:
{transcript}

Important rules:

1. Focus primarily on the visual information.
2. Use the transcript only when it contains clear,
   meaningful spoken information.
3. Ignore random sounds, repeated words, music,
   background noise, and obvious speech-recognition errors.
4. Do not mention that the transcript is noisy or incorrect.
5. Do not invent information.
6. Write only 2 to 3 sentences.
7. Describe the main subject, setting, actions,
   and important events.

Return only the final summary.
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"].strip()