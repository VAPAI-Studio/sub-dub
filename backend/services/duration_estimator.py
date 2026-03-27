import os
import re
import platform

# Ensure espeak-ng is findable on Windows
if platform.system() == "Windows":
    espeak_path = r"C:\Program Files\eSpeak NG"
    if os.path.isdir(espeak_path) and espeak_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = espeak_path + os.pathsep + os.environ.get("PATH", "")

# Speaking rates by language (syllables/second) - University of Lyon 2011 study
SPEAKING_RATES = {
    "es": 7.82, "en": 6.19, "fr": 7.18, "de": 5.97,
    "it": 6.99, "pt": 5.67, "ja": 7.84, "zh": 5.18,
    "ko": 5.97, "ru": 5.38, "ar": 5.22, "hi": 6.09,
    "tr": 6.12, "pl": 5.58, "nl": 5.72, "sv": 5.22,
}

# Cache phonemizer backends by language
_backends = {}


def _get_backend(lang):
    if lang not in _backends:
        try:
            from phonemizer.backend import EspeakBackend
            _backends[lang] = EspeakBackend(lang, preserve_punctuation=False)
        except Exception as e:
            print(f"[ESTIMATOR] Error creando backend para '{lang}': {e}")
            return None
    return _backends[lang]


def count_phonemes(text, lang):
    backend = _get_backend(lang)
    if not backend:
        return None

    try:
        phonemized = backend.phonemize([text], strip=True)
        if not phonemized or not phonemized[0]:
            return None
        # Remove spaces, separators, and stress marks - count only phoneme characters
        cleaned = re.sub(r"[\s\.\,\-\|ˈˌː]", "", phonemized[0])
        return len(cleaned)
    except Exception as e:
        print(f"[ESTIMATOR] Error contando fonemas: {e}")
        return None


def estimate_elevenlabs_speed(source_text, source_duration, target_text, source_lang, target_lang):
    """
    Estimate the optimal ElevenLabs speed parameter (0.7-1.2) based on
    phoneme ratio and language speaking rate differences.

    Returns 1.0 if estimation fails or is not needed.
    """
    if source_duration <= 0:
        return 1.0

    src_phonemes = count_phonemes(source_text, source_lang)
    tgt_phonemes = count_phonemes(target_text, target_lang)

    if not src_phonemes or not tgt_phonemes:
        # Fallback: use character count ratio
        src_len = len(source_text.strip())
        tgt_len = len(target_text.strip())
        if src_len == 0:
            return 1.0
        phoneme_ratio = tgt_len / src_len
    else:
        phoneme_ratio = tgt_phonemes / src_phonemes

    # Adjust for natural speaking rate differences between languages
    src_rate = SPEAKING_RATES.get(source_lang, 6.0)
    tgt_rate = SPEAKING_RATES.get(target_lang, 6.0)
    lang_adjustment = src_rate / tgt_rate

    duration_ratio = phoneme_ratio * lang_adjustment

    print(f"[ESTIMATOR] Fonemas src: {src_phonemes}, tgt: {tgt_phonemes} | "
          f"Ratio: {phoneme_ratio:.2f} | Lang adj: {lang_adjustment:.2f} | "
          f"Duration ratio: {duration_ratio:.2f}")

    # Decide speed
    if duration_ratio > 1.15:
        speed = min(duration_ratio, 1.2)
    elif duration_ratio < 0.8:
        speed = max(duration_ratio, 0.7)
    else:
        speed = 1.0

    return round(speed, 2)
