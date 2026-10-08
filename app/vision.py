import base64
import requests
import cv2


OLLAMA_URL = "http://localhost:11434"
VISION_MODEL = "gemma3:4b"


def describe_frame(frame):

    success, buffer = cv2.imencode(".jpg", frame)

    if not success:
        raise ValueError("Could not encode frame")

    image_base64 = base64.b64encode(
        buffer
    ).decode("utf-8")


    response = requests.post(
        f"{OLLAMA_URL}/api/generate",

        json={
            "model": VISION_MODEL,

            "prompt": """
Describe this video frame in 1 or 2 short sentences.

Mention only clearly visible:
- main subjects
- important objects
- actions
- surroundings

Do not guess names, movie characters, brands,
locations, or events.

Do not use labels such as:
Subject:
Environment:
Color:
Action:

Return only the short description.
""",

            "images": [image_base64],

            "stream": False
        }
    )


    response.raise_for_status()


    return response.json()["response"].strip()