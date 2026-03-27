import os

import torch
from dotenv import load_dotenv

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
INPUTS_DIR = os.path.join(UPLOAD_DIR, "inputs")
DUBS_DIR = os.path.join(UPLOAD_DIR, "dubs")
os.makedirs(INPUTS_DIR, exist_ok=True)
os.makedirs(DUBS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm", ".mp4", ".wma"}
VALID_MODELS = {"tiny", "base", "small", "medium", "large-v2", "large-v3"}

TRANSLATION_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "zh": "Chinese (Simplified)",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
    "pl": "Polish",
    "nl": "Dutch",
    "sv": "Swedish",
}
