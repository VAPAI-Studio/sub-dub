import base64
import io
import os
import numpy as np
import librosa

from elevenlabs import ElevenLabs
from pydub import AudioSegment


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


def generate_dub(segments, voice_map, default_voice_id=None, target_language=None):
    client = get_client()

    total_duration_ms = int(segments[-1].end * 1000)
    final_audio = AudioSegment.silent(duration=total_duration_ms)

    print(f"\n[DUB] Iniciando generación de dub - Total segmentos: {len(segments)}")
    print(f"[DUB] Voice map: {voice_map}")
    print(f"[DUB] Target language: {target_language}")
    print(f"[DUB] Duración total: {total_duration_ms}ms\n")

    for idx, seg in enumerate(segments):
        text = seg.text.strip()
        if not text:
            continue

        # Resolver voz
        voice_id = voice_map.get(seg.speaker or "", default_voice_id)
        if not voice_id:
            voice_id = next(iter(voice_map.values()), None)
        if not voice_id:
            raise ValueError("No se asignó ninguna voz")

        print(f"[SEG {idx}] Speaker: {seg.speaker} | Voice ID: {voice_id}")
        print(f"[SEG {idx}] Texto: '{text}'")
        print(f"[SEG {idx}] Timing: {seg.start:.2f}s - {seg.end:.2f}s (duración: {seg.end - seg.start:.2f}s)")

        # Generar TTS
        response = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            language_code=target_language,
            output_format="mp3_44100_128",
        )

        audio_bytes = base64.b64decode(response.audio_base_64)
        tts_audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))

        print(f"[SEG {idx}] Audio generado: {len(tts_audio)}ms")

        # Ajustar timing
        segment_duration_ms = int((seg.end - seg.start) * 1000)
        if segment_duration_ms <= 0:
            continue

        if len(tts_audio) > segment_duration_ms:
            speed_factor = min(len(tts_audio) / segment_duration_ms, 1.8)
            print(f"[SEG {idx}] ⚠️  ACELERANDO: Audio ({len(tts_audio)}ms) > Segmento ({segment_duration_ms}ms)")
            print(f"[SEG {idx}] Speed factor: {speed_factor:.2f}x (SIN cambiar pitch - librosa)")

            # Convertir AudioSegment a numpy array
            samples = np.array(tts_audio.get_array_of_samples(), dtype=np.float32)
            samples = samples / (2**15)  # Normalizar de int16 a float32

            # Si es estéreo, separar canales
            if tts_audio.channels == 2:
                samples = samples.reshape((-1, 2))
                left = librosa.effects.time_stretch(samples[:, 0], rate=speed_factor)
                right = librosa.effects.time_stretch(samples[:, 1], rate=speed_factor)
                stretched = np.column_stack((left, right))
            else:
                stretched = librosa.effects.time_stretch(samples, rate=speed_factor)

            # Convertir de vuelta a AudioSegment
            stretched = np.clip(stretched, -1.0, 1.0)  # Evitar clipping
            stretched = (stretched * (2**15)).astype(np.int16)
            tts_audio = AudioSegment(
                stretched.tobytes(),
                frame_rate=tts_audio.frame_rate,
                sample_width=2,
                channels=tts_audio.channels
            )

        if len(tts_audio) > segment_duration_ms:
            print(f"[SEG {idx}] ✂️  RECORTANDO: {len(tts_audio)}ms → {segment_duration_ms}ms")
            tts_audio = tts_audio[:segment_duration_ms]

        position_ms = int(seg.start * 1000)
        final_audio = final_audio.overlay(tts_audio, position=position_ms)
        print(f"[SEG {idx}] ✓ Insertado en posición {position_ms}ms\n")

    # Exportar
    output = io.BytesIO()
    final_audio.export(output, format="mp3", bitrate="192k")
    output.seek(0)
    return output
