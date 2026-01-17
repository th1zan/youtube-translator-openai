#!/usr/bin/env python3
"""
Traducteur YouTube : Anglais → Français avec locuteurs distincts
Utilise Google Cloud APIs avec voix premium Wavenet
"""

import os
import sys
import io
from pathlib import Path
from google.cloud import speech, translate_v2, texttospeech
from pydub import AudioSegment
import yt_dlp
from config import Config


def test_basic_connectivity():
    """Test minimal de connexion aux APIs Google"""
    try:
        speech.SpeechClient()
        translate_v2.Client()
        texttospeech.TextToSpeechClient()
        print("✅ Connexion Google Cloud APIs: OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print(
            "Vérifiez vos variables d'environnement GOOGLE_APPLICATION_CREDENTIALS et GOOGLE_CLOUD_PROJECT"
        )
        return False


def download_audio(url):
    """Télécharge l'audio YouTube avec métadonnées"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "extract_flat": False,
        "writeinfojson": True,
        "writethumbnail": False,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Impossible d'extraire les informations de la vidéo")

            audio_file = f"temp_audio.{info.get('ext', 'mp3')}"
            metadata = {
                "title": info.get("title", "Unknown Title"),
                "uploader": info.get("uploader", "Unknown Uploader"),
                "duration": info.get("duration", 0),
                "description": info.get("description", "")[:200]
                if info.get("description")
                else "",
            }
            print(f"✅ Audio téléchargé: {audio_file}")
            return audio_file, metadata
    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        sys.exit(1)


def transcribe_with_diarization(audio_file):
    """Transcrit avec séparation des locuteurs"""
    client = speech.SpeechClient()

    try:
        with open(audio_file, "rb") as audio:
            content = audio.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            language_code="en-US",
            enable_speaker_diarization=True,
            diarization_speaker_count=2,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        print("⏳ Transcription en cours...")
        response = operation.result(timeout=Config.API_TIMEOUT)

        if not response or not hasattr(response, "results"):
            raise Exception("Réponse de transcription invalide")

        segments = []
        for result in response.results:
            if not result.alternatives:
                continue
            for word in result.alternatives[0].words:
                segments.append(
                    {
                        "word": word.word,
                        "start_time": word.start_time.total_seconds(),
                        "end_time": word.end_time.total_seconds(),
                        "speaker": word.speaker_tag,
                    }
                )

        print(
            f"✅ Transcription terminée: {len(segments)} mots, {len(set(s['speaker'] for s in segments))} locuteurs"
        )
        return segments

    except Exception as e:
        print(f"❌ Erreur transcription: {e}")
        sys.exit(1)


def group_segments_by_speaker(segments):
    """Regroupe les mots par locuteur avec timings"""
    grouped = []
    current_speaker = None
    current_words = []
    current_start = 0

    for segment in segments:
        if segment["speaker"] != current_speaker:
            if current_words:
                grouped.append(
                    {
                        "speaker": current_speaker,
                        "text": " ".join(current_words),
                        "start_time": current_start,
                        "end_time": segment["start_time"] - 0.1,
                    }
                )

            current_speaker = segment["speaker"]
            current_words = [segment["word"]]
            current_start = segment["start_time"]
        else:
            current_words.append(segment["word"])

    # Dernier segment
    if current_words:
        grouped.append(
            {
                "speaker": current_speaker,
                "text": " ".join(current_words),
                "start_time": current_start,
                "end_time": segments[-1]["end_time"] if segments else current_start + 1,
            }
        )

    return grouped


def translate_segments(segments):
    """Traduit chaque segment en français"""
    client = translate_v2.Client()
    translated = []

    print("⏳ Traduction en cours...")
    for segment in segments:
        try:
            result = client.translate(
                segment["text"], source_language="en", target_language="fr"
            )
            translated.append({**segment, "text_fr": result["translatedText"]})
        except Exception as e:
            print(f"⚠️ Erreur traduction segment: {e}")
            translated.append(
                {
                    **segment,
                    "text_fr": segment["text"],  # Fallback
                }
            )

    print(f"✅ Traduction terminée: {len(translated)} segments")
    return translated


def generate_premium_tts(text, speaker_id):
    """Génère audio TTS avec voix premium"""
    client = texttospeech.TextToSpeechClient()

    voice_name = Config.VOICES.get(speaker_id, Config.VOICES[1])

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="fr-FR", name=voice_name)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1.0
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content


def assemble_final_audio(translated_segments):
    """Assemble l'audio final avec pauses préservées"""
    final_audio = AudioSegment.empty()
    current_time = 0

    print("⏳ Génération audio TTS...")
    for i, segment in enumerate(translated_segments):
        # Calculer le silence nécessaire
        silence_duration = (segment["start_time"] - current_time) * 1000
        if silence_duration > Config.MIN_SILENCE_MS:
            silence = AudioSegment.silent(duration=silence_duration)
            final_audio += silence

        # Générer TTS
        try:
            tts_audio_data = generate_premium_tts(
                segment["text_fr"], segment["speaker"]
            )
            tts_segment = AudioSegment.from_mp3(io.BytesIO(tts_audio_data))
            final_audio += tts_segment
            current_time = segment["end_time"]

            print(
                f"  Segment {i + 1}/{len(translated_segments)}: Locuteur {segment['speaker']}"
            )

        except Exception as e:
            print(f"⚠️ Erreur TTS segment {i + 1}: {e}")
            continue

    print("✅ Audio assemblé")
    return final_audio


def export_with_metadata(audio, metadata, output_name=None):
    """Exporte le MP3 final avec métadonnées"""
    if not output_name:
        safe_title = metadata["title"].replace("/", "_").replace("\\", "_")
        output_name = f"{safe_title}_traduit.mp3"

    # Tags ID3
    tags = {
        "title": f"{metadata['title']} (Traduit FR)",
        "artist": metadata["uploader"],
        "album": "Traduction automatique YouTube",
        "comment": f"Traduit automatiquement anglais→français. Durée originale: {metadata['duration']}s. Voix premium Google Wavenet.",
        "genre": "Speech",
        "year": "2025",
    }

    audio.export(output_name, format="mp3", tags=tags)
    print(f"✅ Fichier créé: {output_name}")
    return output_name


def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    for file in Path(".").glob("temp_audio.*"):
        file.unlink(missing_ok=True)
    for file in Path(".").glob("*.json"):
        if "info" in file.name:
            file.unlink(missing_ok=True)


def main(url):
    """Fonction principale"""
    print("🎵 Traducteur YouTube: Anglais → Français")
    print("=" * 50)

    # Test de connexion
    if not test_basic_connectivity():
        sys.exit(1)

    try:
        # Téléchargement
        audio_file, metadata = download_audio(url)

        # Transcription
        segments = transcribe_with_diarization(audio_file)

        # Regroupement
        grouped_segments = group_segments_by_speaker(segments)

        # Traduction
        translated_segments = translate_segments(grouped_segments)

        # Génération audio
        final_audio = assemble_final_audio(translated_segments)

        # Export final
        output_file = export_with_metadata(final_audio, metadata)

        # Nettoyage
        cleanup_temp_files()

        print(f"🎉 Traduction terminée avec succès!")
        print(f"📁 Fichier: {output_file}")

    except KeyboardInterrupt:
        print("\n⏹️ Interrompu par l'utilisateur")
        cleanup_temp_files()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        cleanup_temp_files()
        sys.exit(1)


if __name__ == "__main__":
    import io  # Pour BytesIO dans TTS

    if len(sys.argv) != 2:
        print("Usage: uv run python translate_youtube.py 'https://youtu.be/VIDEO_ID'")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
