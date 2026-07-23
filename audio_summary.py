"""
Live Coding: Audio Pipeline para el resumen de audios.
Este script demuestra cómo extraer información de audios
utilizando 'whisper' y resumiendolo con 'gpt-4o-mini'.
"""

import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
import jiwer


load_dotenv()
TRANSCRIPTION_MODEL = "gpt-4o-transcribe" #"whisper-1"
SUMMARY_MODEL = "gpt-4o-mini"
TTS_MODEL = "gpt-4o-mini-tts"


def transcribe_audio(client: OpenAI, audio_path: str) -> str | None:
    """Transcribe un archivo de audio."""
    # --- Run ASR (Transcription) ---
    if not os.path.exists(audio_path):
        print(f"❌ Error: No se encuentra el archivo de audio en {audio_path}")
        return None

    print(f"🎙️ Transcribiendo audio...")
    try:
        with open(audio_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model=TRANSCRIPTION_MODEL,
                file=audio_file,
                language="es",
                response_format="text"
            )
        transcript = transcript_response.strip()
    except Exception as e:
        print(f"❌ Error durante la transcripción: {e}")
        return None

    print("\n📝 Transcripción obtenida:")
    print("-" * 30)
    print(transcript)
    print("-" * 30)

    if not transcript:
        print("\n⚠️ Advertencia: La API devolvió una transcripción vacía.")

    return transcript


def summarize_transcript(client: OpenAI, transcript: str) -> str | None:
    """Genera un resumen breve de una transcripción."""
    # --- Run Summarization ---
    print("\n🧠 Generando resumen...")
    try:
        response = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un asistente encargado de resumir transcripciones de audio de forma concisa y clara en español."
                },
                {
                    "role": "user", 
                    "content": f"Por favor, resume el siguiente texto extraído de un audio en 25 palabras como máximo:\n\n{transcript}"
                }
            ],
            temperature=0.7,
            max_tokens=35
        )
        summary_text = response.choices[0].message.content.strip() # type: ignore
    except Exception as e:
        print(f"❌ Error durante el resumen: {e}")
        return None

    print("\n✨ Resumen del audio:")
    print("=" * 30)
    print(summary_text)
    print("=" * 30)

    return summary_text


def convert_summary_to_speech(
    client: OpenAI, summary_text: str, audio_path: str
) -> None:
    """Convierte el resumen en un archivo wav."""
    # --- Convert Summary to Speech ---
    summary_audio_path = f"{os.path.splitext(audio_path)[0]}_summary.wav"
    print("\n🔊 Convirtiendo resumen a audio...")
    try:
        audio_response = client.audio.speech.create(
            model=TTS_MODEL,
            voice="coral",
            input=summary_text,
            instructions="Habla en español rioplatense con un tono claro y natural."
        )
        audio_response.write_to_file(summary_audio_path)
        print(f"✅ Audio del resumen guardado en: {summary_audio_path}")
    except Exception as e:
        print(f"❌ Error durante la generación del audio: {e}")


def audio_pipeline(audio_path: str) -> str | None:
    """Pipeline para transcribir, resumir y generar audio."""

    print(f"\n🚀 Iniciando pipeline de audio: {os.path.basename(audio_path)}")

    # Initialize OpenAI client
    client = OpenAI()

    transcript = transcribe_audio(client, audio_path)
    if not transcript:
        return transcript

    summary_text = summarize_transcript(client, transcript)
    if summary_text:
        convert_summary_to_speech(client, summary_text, audio_path)

    return transcript


def evaluate_wer(original_text: str, transcript_text: str) -> float:

    # Normalizamos textos para no penalizar por mayúsculas o comas
    transformacion = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip()
    ])

    original_norm = transformacion(original_text)
    transcrito_norm = transformacion(transcript_text)

    # Calculamos el error matemático
    wer_score = jiwer.wer(original_norm, transcrito_norm)
    medidas = jiwer.process_words(original_norm, transcrito_norm)

    print("\n✨ Evaluación WER de la transcripción")
    print("=" * 40)
    print(f"Texto original : {original_norm}")
    print(f"Texto transcrito: {transcrito_norm}")
    print("-" * 40)
    print(f"Word Error Rate (WER) : {wer_score * 100:.2f}%")
    print(f"Sustituciones (S)      : {medidas.substitutions}")
    print(f"Inserciones (I)        : {medidas.insertions}")
    print(f"Eliminaciones (D)      : {medidas.deletions}")
    print("=" * 40)

    return wer_score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe and summarize an audio file using OpenAI APIs."
    )
    parser.add_argument(
        "--audio",
        type=str,
        default="resources/demo.wav",
        help="Path to the audio file (default: resources/demo.wav)"
    )
    parser.add_argument(
        "--wer",
        type=str,
        default=None,
        help="Path to a TXT file containing the original reference transcript for WER evaluation."
    )
    args = parser.parse_args()

    transcript = audio_pipeline(audio_path=args.audio)

    if args.wer:
        if not os.path.exists(args.wer):
            print(f"❌ Error: No se encuentra el archivo de referencia WER en {args.wer}")
        elif transcript is None:
            print("❌ No se pudo obtener la transcripción para evaluar WER.")
        else:
            with open(args.wer, "r", encoding="utf-8") as ref_file:
                original_text = ref_file.read()
            evaluate_wer(original_text, transcript)
