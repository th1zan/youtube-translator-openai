#!/usr/bin/env python3
"""
Traducteur YouTube complet avec manipulation audio via ffmpeg
Alternative à pydub pour éviter les problèmes de dépendances
"""

import os
import sys
import io
import subprocess
import tempfile
from pathlib import Path
from google.cloud import speech, translate_v2, texttospeech
import yt_dlp


def test_basic_connectivity():
    """Test de connexion aux APIs Google"""
    try:
        speech.SpeechClient()
        translate_v2.Client()
        texttospeech.TextToSpeechClient()
        print("✅ Connexion Google Cloud APIs: OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def download_audio(url):
    """Télécharge l'audio YouTube"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "extract_flat": False,
        "writeinfojson": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Impossible d'extraire les informations de la vidéo")

            ext = info.get("ext", "mp3")
            audio_file = f"temp_audio.{ext}"
            metadata = {
                "title": info.get("title", "Unknown Title"),
                "uploader": info.get("uploader", "Unknown Uploader"),
                "duration": info.get("duration", 0),
            }
            print(f"✅ Audio téléchargé: {metadata['title']}")
            return audio_file, metadata
    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        sys.exit(1)


def convert_to_wav(input_file):
    """Convertit l'audio en WAV mono pour Google Speech-to-Text"""
    output_file = "temp_audio_mono.wav"

    try:
        # Convertir en WAV mono 16kHz (format requis par Google)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-ac",
            "1",  # Mono
            "-ar",
            "16000",  # 16kHz
            "-acodec",
            "pcm_s16le",  # WAV format
            output_file,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Erreur ffmpeg: {result.stderr}")
            # Si ffmpeg échoue, essayer de continuer avec le fichier original
            return input_file

        print("✅ Conversion audio: WAV mono 16kHz")
        return output_file

    except FileNotFoundError:
        print("⚠️ ffmpeg non trouvé, utilisation du fichier original")
        return input_file


def transcribe_with_diarization(audio_file):
    """Transcrit avec séparation des locuteurs (version simplifiée pour test)"""
    client = speech.SpeechClient()

    try:
        # Pour l'instant, transcription basique (limite Google Cloud)
        # TODO: Implémenter GCS pour fichiers longs + diarization

        with open(audio_file, "rb") as audio:
            content = audio.read()

        # Limiter à 60 secondes pour éviter la limite
        audio = speech.RecognitionAudio(content=content[: 60 * 16000 * 2])  # 60s max

        config = speech.RecognitionConfig(
            language_code="en-US",
            enable_automatic_punctuation=True,
        )

        response = client.recognize(config=config, audio=audio)

        if response.results and len(response.results) > 0:
            text = response.results[0].alternatives[0].transcript

            # Simulation de segments avec 2 locuteurs (basique)
            # TODO: Implémenter vraie diarization avec GCS
            segments = [
                {
                    "word": word,
                    "start_time": i * 0.5,
                    "end_time": (i + 1) * 0.5,
                    "speaker": 1 if i % 2 == 0 else 2,  # Alternance simple
                }
                for i, word in enumerate(text.split())
            ]

            print(
                f"✅ Transcription basique: {len(segments)} mots (simulation diarization)"
            )
            print(f"   Texte: {text[:100]}...")

            return segments
        else:
            raise Exception("Aucune transcription obtenue")

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


def generate_tts_audio(segments, output_dir="temp_tts_segments"):
    """Génère les fichiers TTS pour chaque segment"""
    Path(output_dir).mkdir(exist_ok=True)

    print("⏳ Génération audio TTS...")
    tts_files = []

    for i, segment in enumerate(segments):
        try:
            client = texttospeech.TextToSpeechClient()

            voice_name = (
                "fr-FR-Wavenet-A" if segment["speaker"] == 1 else "fr-FR-Wavenet-E"
            )

            synthesis_input = texttospeech.SynthesisInput(text=segment["text_fr"])
            voice = texttospeech.VoiceSelectionParams(
                language_code="fr-FR", name=voice_name
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            tts_file = f"{output_dir}/segment_{i:03d}_speaker_{segment['speaker']}.mp3"
            with open(tts_file, "wb") as f:
                f.write(response.audio_content)

            tts_files.append((tts_file, segment["start_time"]))
            print(f"  Segment {i + 1}/{len(segments)}: Locuteur {segment['speaker']}")

        except Exception as e:
            print(f"⚠️ Erreur TTS segment {i + 1}: {e}")
            continue

    print("✅ Audio TTS généré")
    return tts_files


def concatenate_audio_files(tts_files, output_file):
    """Concatène les fichiers audio avec ffmpeg"""
    try:
        # Créer une liste de fichiers pour ffmpeg
        concat_file = "temp_concat.txt"
        with open(concat_file, "w") as f:
            for tts_file, _ in tts_files:
                f.write(f"file '{tts_file}'\n")

        # Concaténer avec ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-c",
            "copy",
            output_file,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Erreur ffmpeg concat: {result.stderr}")
            return False

        # Nettoyer
        os.remove(concat_file)
        print(f"✅ Audio final: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Erreur concaténation: {e}")
        return False


def add_metadata_to_mp3(input_file, output_file, metadata):
    """Ajoute les métadonnées ID3 au fichier MP3"""
    try:
        # Utiliser ffmpeg pour ajouter les métadonnées
        title = metadata["title"].replace("'", "\\'")[:100]
        artist = metadata["uploader"].replace("'", "\\'")[:100]

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-metadata",
            f"title={title} (Traduit)",
            "-metadata",
            f"artist={artist}",
            "-metadata",
            "album=Traduction automatique YouTube",
            "-metadata",
            f"comment=Traduit automatiquement anglais→français. Durée originale: {metadata['duration']}s. Voix premium Google Wavenet.",
            "-metadata",
            "genre=Speech",
            "-codec",
            "copy",
            output_file,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Erreur métadonnées: {result.stderr}")
            # Copier quand même le fichier
            import shutil

            shutil.copy(input_file, output_file)
        else:
            print("✅ Métadonnées ajoutées")

    except Exception as e:
        print(f"⚠️ Erreur métadonnées: {e}")
        # Copier quand même le fichier
        import shutil

        shutil.copy(input_file, output_file)


def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    temp_files = [
        "temp_audio.mp3",
        "temp_audio.m4a",
        "temp_audio.webm",
        "temp_audio.wav",
        "temp_audio_mono.wav",
        "temp_concat.txt",
    ]

    # Supprimer les fichiers individuels
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)

    # Supprimer le répertoire TTS
    import shutil

    if os.path.exists("temp_tts_segments"):
        shutil.rmtree("temp_tts_segments")

    # Supprimer les fichiers JSON de yt-dlp
    for file in Path(".").glob("*.json"):
        if "info" in file.name or "temp_audio" in file.name:
            file.unlink(missing_ok=True)

    print("🧹 Nettoyage terminé")


def main(url):
    """Fonction principale"""
    print("🎵 Traducteur YouTube Complet avec ffmpeg")
    print("=" * 50)

    # Test de connexion
    if not test_basic_connectivity():
        return

    try:
        # Téléchargement
        audio_file, metadata = download_audio(url)

        # Conversion pour Google
        wav_file = convert_to_wav(audio_file)

        # Transcription
        segments = transcribe_with_diarization(wav_file)

        # Regroupement
        grouped_segments = group_segments_by_speaker(segments)

        # Traduction
        translated_segments = translate_segments(grouped_segments)

        # Génération TTS
        tts_files = generate_tts_audio(translated_segments)

        # Assemblage final
        temp_output = "temp_final.mp3"
        if concatenate_audio_files(tts_files, temp_output):
            # Métadonnées
            safe_title = metadata["title"].replace("/", "_").replace("\\", "_")
            final_output = f"output/{safe_title}_traduit.mp3"
            add_metadata_to_mp3(temp_output, final_output, metadata)

            # Nettoyage
            cleanup_temp_files()
            if os.path.exists(temp_output):
                os.remove(temp_output)

            print(f"🎉 Traduction terminée avec succès!")
            print(f"📁 Fichier: {final_output}")
            print(
                f"📊 Stats: {len(translated_segments)} segments, {len(set(s['speaker'] for s in translated_segments))} locuteurs"
            )
        else:
            print("❌ Échec de l'assemblage audio")

    except KeyboardInterrupt:
        print("\n⏹️ Interrompu par l'utilisateur")
        cleanup_temp_files()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        cleanup_temp_files()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: uv run python translate_youtube_complete.py 'https://youtu.be/VIDEO_ID'"
        )
        sys.exit(1)

    url = sys.argv[1]
    main(url)
