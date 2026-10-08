import requests

OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "gemma3:4b"


def create_chapters(visual_descriptions):

    scenes = "\n".join(
        f"{item['timestamp']:.2f} seconds - {item['description']}"
        for item in visual_descriptions
    )

    prompt = f"""
Create a short chapter title for each video scene below.

Scenes:
{scenes}

Rules:
- Return exactly one title for each scene.
- Use 3 to 7 words per title.
- Keep the same order as the scenes.
- Do not add information that is not present.
- Return only the titles, one per line.

Example:
Rabbit in the Burrow
Rabbit and Butterfly
White Rabbit in Field
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

    titles = response.json()["response"].strip().splitlines()

    chapters = []

    for item, title in zip(visual_descriptions, titles):

        chapters.append({
            "timestamp": item["timestamp"],
            "title": title.strip()
        })

    return chapters