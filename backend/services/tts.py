import base64
import io
import os
import numpy as np
import librosa

from elevenlabs import ElevenLabs, VoiceSettings
from pydub import AudioSegment

from services.duration_estimator import estimate_elevenlabs_speed


def get_client():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY no configurado en el backend (.env)")
    return ElevenLabs(api_key=api_key)


def list_voices():
    client = get_client()
    response = client.voices.get_all()

    return [
        {
            "voice_id": v.voice_id,
            "name": v.name,
            "gender": (v.labels or {}).get("gender", ""),
            "accent": (v.labels or {}).get("accent", ""),
            "age": (v.labels or {}).get("age", ""),
            "language": (v.labels or {}).get("language", ""),
        }
        for v in response.voices
    ]


def list_library_voices(language=None, page_size=50):
    client = get_client()
    response = client.voices.get_shared(
        language=language,
        page_size=page_size,
        sort="trending",
    )

    return [
        {
            "voice_id": v.voice_id,
            "name": v.name,
            "gender": v.gender or "",
            "accent": v.accent or "",
            "age": v.age or "",
            "language": v.language or "",
            "category": v.category or "",
            "preview_url": v.preview_url or "",
        }
        for v in response.voices
    ]


def _merge_short_segments(segments, min_duration_ms=300):
    """Merge segments shorter than min_duration_ms with adjacent same-speaker segments."""
    if not segments:
        return segments

    merged = []
    i = 0
    while i < len(segments):
        seg = segments[i]
        duration_ms = int((seg.end - seg.start) * 1000)

        if duration_ms < min_duration_ms and i + 1 < len(segments):
            next_seg = segments[i + 1]
            if (seg.speaker or "") == (next_seg.speaker or ""):
                # Merge with next segment
                print(f"[MERGE] Fusionando SEG {i} ({duration_ms}ms, '{seg.text.strip()}') "
                      f"con SEG {i+1} ('{next_seg.text.strip()}')")

                class MergedSegment:
                    pass

                m = MergedSegment()
                m.start = seg.start
                m.end = next_seg.end
                m.text = seg.text.strip() + " " + next_seg.text.strip()
                m.speaker = seg.speaker
                m.original_text = None
                if hasattr(seg, 'original_text') and seg.original_text and hasattr(next_seg, 'original_text') and next_seg.original_text:
                    m.original_text = seg.original_text.strip() + " " + next_seg.original_text.strip()
                elif hasattr(seg, 'original_text') and seg.original_text:
                    m.original_text = seg.original_text
                elif hasattr(next_seg, 'original_text') and next_seg.original_text:
                    m.original_text = next_seg.original_text

                merged.append(m)
                i += 2
                continue

        merged.append(seg)
        i += 1

    return merged


def _generate_tts_segment(client, voice_id, text, target_language, speed=1.0):
    """Generate TTS audio for a single segment."""
    from elevenlabs.core.api_error import ApiError
    try:
        response = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            language_code=target_language,
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(speed=speed),
        )
    except ApiError as e:
        body = getattr(e, 'body', {}) or {}
        detail = body.get('detail', {}) if isinstance(body, dict) else {}
        status = detail.get('status', '') if isinstance(detail, dict) else ''
        if status == 'quota_exceeded':
            raise ValueError("Sin créditos en ElevenLabs. Recarga tu cuenta para continuar.")
        raise ValueError(f"Error de ElevenLabs: {detail.get('message', str(e))}" if isinstance(detail, dict) else str(e))
    audio_bytes = base64.b64decode(response.audio_base_64)
    return AudioSegment.from_mp3(io.BytesIO(audio_bytes))


def _resolve_voice(seg, voice_map, default_voice_id):
    """Resolve voice ID for a segment."""
    voice_id = voice_map.get(seg.speaker or "", default_voice_id)
    if not voice_id:
        voice_id = next(iter(voice_map.values()), None)
    if not voice_id:
        raise ValueError("No se asignó ninguna voz")
    return voice_id


def generate_dub(segments, voice_map, default_voice_id=None, target_language=None, source_language=None, timing_mode="strict"):
    client = get_client()

    # Merge very short segments before processing (not needed for free mode)
    if timing_mode != "free":
        segments = _merge_short_segments(list(segments))
    else:
        segments = list(segments)

    print(f"\n[DUB] Iniciando generación de dub - Total segmentos: {len(segments)}")
    print(f"[DUB] Voice map: {voice_map}")
    print(f"[DUB] Target language: {target_language}")
    print(f"[DUB] Source language: {source_language}")
    print(f"[DUB] Timing mode: {timing_mode}\n")

    if timing_mode == "free":
        return _generate_dub_free(client, segments, voice_map, default_voice_id, target_language)
    elif timing_mode == "natural":
        return _generate_dub_natural(client, segments, voice_map, default_voice_id, target_language)
    else:
        return _generate_dub_strict(client, segments, voice_map, default_voice_id, target_language, source_language)


def _generate_dub_strict(client, segments, voice_map, default_voice_id, target_language, source_language):
    """Strict mode: fit audio into original timeline slots."""
    total_duration_ms = int(segments[-1].end * 1000)
    final_audio = AudioSegment.silent(duration=total_duration_ms)

    for idx, seg in enumerate(segments):
        text = seg.text.strip()
        if not text:
            continue

        voice_id = _resolve_voice(seg, voice_map, default_voice_id)

        print(f"[SEG {idx}] Speaker: {seg.speaker} | Voice ID: {voice_id}")
        print(f"[SEG {idx}] Texto: '{text}'")
        print(f"[SEG {idx}] Timing: {seg.start:.2f}s - {seg.end:.2f}s (duración: {seg.end - seg.start:.2f}s)")

        # Estimate optimal ElevenLabs speed
        speed = 1.0
        original_text = getattr(seg, 'original_text', None)
        if source_language and target_language and original_text:
            speed = estimate_elevenlabs_speed(
                original_text, seg.end - seg.start, text, source_language, target_language
            )
        print(f"[SEG {idx}] Speed ElevenLabs: {speed:.2f}x")

        tts_audio = _generate_tts_segment(client, voice_id, text, target_language, speed)
        print(f"[SEG {idx}] Audio generado: {len(tts_audio)}ms")

        segment_duration_ms = int((seg.end - seg.start) * 1000)
        if segment_duration_ms <= 0:
            continue

        # Calculate max allowed duration (allow overflow into gap before next segment)
        if idx + 1 < len(segments):
            gap_ms = int((segments[idx + 1].start - seg.end) * 1000)
            max_allowed_ms = segment_duration_ms + max(0, gap_ms)
        else:
            max_allowed_ms = segment_duration_ms

        if len(tts_audio) > max_allowed_ms:
            speed_factor = min(len(tts_audio) / max_allowed_ms, 1.8)
            print(f"[SEG {idx}] ⚠️  ACELERANDO: Audio ({len(tts_audio)}ms) > Max permitido ({max_allowed_ms}ms)")
            print(f"[SEG {idx}] Speed factor librosa: {speed_factor:.2f}x (SIN cambiar pitch)")

            samples = np.array(tts_audio.get_array_of_samples(), dtype=np.float32)
            samples = samples / (2**15)

            if tts_audio.channels == 2:
                samples = samples.reshape((-1, 2))
                left = librosa.effects.time_stretch(samples[:, 0], rate=speed_factor)
                right = librosa.effects.time_stretch(samples[:, 1], rate=speed_factor)
                stretched = np.column_stack((left, right))
            else:
                stretched = librosa.effects.time_stretch(samples, rate=speed_factor)

            stretched = np.clip(stretched, -1.0, 1.0)
            stretched = (stretched * (2**15)).astype(np.int16)
            tts_audio = AudioSegment(
                stretched.tobytes(),
                frame_rate=tts_audio.frame_rate,
                sample_width=2,
                channels=tts_audio.channels
            )
        elif len(tts_audio) > segment_duration_ms:
            print(f"[SEG {idx}] ↗️  DESBORDE PERMITIDO: Audio ({len(tts_audio)}ms) usa gap disponible ({max_allowed_ms}ms)")

        if len(tts_audio) > max_allowed_ms:
            print(f"[SEG {idx}] ✂️  RECORTANDO: {len(tts_audio)}ms → {max_allowed_ms}ms")
            tts_audio = tts_audio[:max_allowed_ms]

        position_ms = int(seg.start * 1000)
        final_audio = final_audio.overlay(tts_audio, position=position_ms)
        print(f"[SEG {idx}] ✓ Insertado en posición {position_ms}ms\n")

    output = io.BytesIO()
    final_audio.export(output, format="mp3", bitrate="192k")
    output.seek(0)
    return output


def _generate_dub_natural(client, segments, voice_map, default_voice_id, target_language):
    """Natural mode: position at original timestamps but don't speed up or trim."""
    total_duration_ms = int(segments[-1].end * 1000)
    # Start with original duration, extend if needed
    max_end_ms = total_duration_ms

    generated = []

    for idx, seg in enumerate(segments):
        text = seg.text.strip()
        if not text:
            continue

        voice_id = _resolve_voice(seg, voice_map, default_voice_id)
        print(f"[SEG {idx}] Texto: '{text}' | Posición: {seg.start:.2f}s")

        tts_audio = _generate_tts_segment(client, voice_id, text, target_language)
        print(f"[SEG {idx}] Audio generado: {len(tts_audio)}ms (sin ajustar)")

        position_ms = int(seg.start * 1000)
        end_ms = position_ms + len(tts_audio)
        if end_ms > max_end_ms:
            max_end_ms = end_ms

        generated.append((position_ms, tts_audio))
        print(f"[SEG {idx}] ✓ Insertado en posición {position_ms}ms\n")

    final_audio = AudioSegment.silent(duration=max_end_ms)
    for position_ms, tts_audio in generated:
        final_audio = final_audio.overlay(tts_audio, position=position_ms)

    output = io.BytesIO()
    final_audio.export(output, format="mp3", bitrate="192k")
    output.seek(0)
    return output


def _generate_dub_free(client, segments, voice_map, default_voice_id, target_language):
    """Free mode: concatenate segments sequentially with small gaps."""
    GAP_MS = 300
    generated = []
    cursor_ms = 0

    for idx, seg in enumerate(segments):
        text = seg.text.strip()
        if not text:
            continue

        voice_id = _resolve_voice(seg, voice_map, default_voice_id)
        print(f"[SEG {idx}] Texto: '{text}' | Cursor: {cursor_ms}ms")

        tts_audio = _generate_tts_segment(client, voice_id, text, target_language)
        print(f"[SEG {idx}] Audio generado: {len(tts_audio)}ms")

        generated.append((cursor_ms, tts_audio))
        cursor_ms += len(tts_audio) + GAP_MS
        print(f"[SEG {idx}] ✓ Cursor avanzado a {cursor_ms}ms\n")

    final_audio = AudioSegment.silent(duration=cursor_ms)
    for position_ms, tts_audio in generated:
        final_audio = final_audio.overlay(tts_audio, position=position_ms)

    output = io.BytesIO()
    final_audio.export(output, format="mp3", bitrate="192k")
    output.seek(0)
    return output
