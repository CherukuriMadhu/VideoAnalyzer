import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "local")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

VISION_MODEL = os.getenv(
    "VISION_MODEL",
    "gemma3:4b"
)

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "tiny.en"
)

MAX_FRAMES = int(
    os.getenv("MAX_FRAMES", "8")
)