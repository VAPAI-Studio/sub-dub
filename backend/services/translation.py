import os

import anthropic

from config import TRANSLATION_LANGUAGES


def translate_segments(segments, source_language, target_language):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurado en el backend (.env)")

    if target_language not in TRANSLATION_LANGUAGES:
        raise ValueError(f"Idioma no soportado: {target_language}")

    target_name = TRANSLATION_LANGUAGES[target_language]
    source_name = TRANSLATION_LANGUAGES.get(
        source_language, source_language or "the original language"
    )

    lines = [f"[{i}] {seg.text.strip()}" for i, seg in enumerate(segments)]
    text_block = "\n".join(lines)

    client = anthropic.Anthropic(api_key=api_key, max_retries=5)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""Translate the following subtitles from {source_name} to {target_name}.

Rules:
- Keep the [number] prefix on each line exactly as-is
- Only translate the text after the [number] prefix
- Do not add, remove, or merge lines
- Keep the same tone and register
- Output ONLY the translated lines, nothing else

{text_block}""",
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Parsear respuesta
    translated = {}
    for line in response_text.split("\n"):
        line = line.strip()
        if not line or not line.startswith("["):
            continue
        bracket_end = line.find("]")
        if bracket_end == -1:
            continue
        try:
            idx = int(line[1:bracket_end])
            translated[idx] = line[bracket_end + 1:].strip()
        except ValueError:
            continue

    return [
        {
            "start": seg.start,
            "end": seg.end,
            "text": translated.get(i, seg.text),
            "speaker": seg.speaker,
        }
        for i, seg in enumerate(segments)
    ]
