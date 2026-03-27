import os
from typing import Optional

import whisperx
from whisperx.diarize import DiarizationPipeline

from config import device, compute_type

# Cachés de modelos
_asr_models = {}
_align_models = {}


def get_asr_model(model_size: str):
    if model_size not in _asr_models:
        _asr_models[model_size] = whisperx.load_model(
            model_size, device, compute_type=compute_type
        )
    return _asr_models[model_size]


def get_align_model(language_code: str):
    if language_code not in _align_models:
        model_a, metadata = whisperx.load_align_model(
            language_code=language_code, device=device
        )
        _align_models[language_code] = (model_a, metadata)
    return _align_models[language_code]


def transcribe_audio(file_path: str, model_size: str, language: Optional[str], task: str):
    audio = whisperx.load_audio(file_path)
    model = get_asr_model(model_size)
    lang = None if language == "auto" else language
    result = model.transcribe(audio, batch_size=16, language=lang, task=task)
    return audio, result


def align_audio(audio, result):
    language_code = result.get("language", "unknown")
    model_a, metadata = get_align_model(language_code)
    return whisperx.align(
        result["segments"], model_a, metadata, audio, device,
        return_char_alignments=False,
    )


def diarize_audio(audio, result, min_speakers=None, max_speakers=None):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN no configurado en el backend (.env)")

    pipeline = DiarizationPipeline(token=hf_token, device=device)
    diarize_segments = pipeline(
        audio,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
    )
    return whisperx.assign_word_speakers(diarize_segments, result)


def format_segments(result, include_words: bool):
    segments = []
    for seg in result["segments"]:
        segment_data = {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg.get("text", ""),
        }
        if "speaker" in seg:
            segment_data["speaker"] = seg["speaker"]
        if "words" in seg and include_words:
            segment_data["words"] = [
                {
                    "word": w.get("word", ""),
                    "start": round(w["start"], 2) if "start" in w else None,
                    "end": round(w["end"], 2) if "end" in w else None,
                    "speaker": w.get("speaker"),
                }
                for w in seg["words"]
            ]
        segments.append(segment_data)
    return segments
