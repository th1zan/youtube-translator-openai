#!/usr/bin/env python3
"""
Traducteur YouTube simplifié (sans pydub pour le test)
"""

import os
import sys
import yt_dlp
from google.cloud import speech, translate_v2, texttospeech


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
        "outtmpl": "audio_test.%(ext)s",
        "extract_flat": False,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Impossible d'extraire les informations de la vidéo")

            ext = info.get("ext", "mp3")
            audio_file = f"audio_test.{ext}"
            metadata = {
                "title": info.get("title", "Unknown Title"),
                "uploader": info.get("uploader", "Unknown Uploader"),
                "duration": info.get("duration", 0),
            }
            print(f"✅ Audio téléchargé: {metadata['title']} ({metadata['duration']}s)")
            return audio_file, metadata
    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        sys.exit(1)


def transcribe_sample(audio_file):
    """Transcription basique d'un échantillon (premières secondes)"""
    client = speech.SpeechClient()

    try:
        # Lire seulement les premières secondes pour le test
        with open(audio_file, "rb") as f:
            content = f.read(1024 * 100)  # ~100KB pour test

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            language_code="en-US",
            audio_channel_count=2,  # Spécifier 2 canaux
            enable_automatic_punctuation=True,
        )

        response = client.recognize(config=config, audio=audio)

        if response.results and len(response.results) > 0:
            text = response.results[0].alternatives[0].transcript
            print(f"✅ Transcription test: {text[:100]}...")
            return text
        else:
            print("⚠️ Aucune transcription obtenue")
            return ""

    except Exception as e:
        print(f"❌ Erreur transcription: {e}")
        return ""


def translate_sample(text):
    """Traduction basique"""
    if not text:
        return ""

    try:
        client = translate_v2.Client()
        result = client.translate(text, target_language="fr")
        translated = result.get("translatedText", "")
        print(f"✅ Traduction test: {translated[:100]}...")
        return translated
    except Exception as e:
        print(f"❌ Erreur traduction: {e}")
        return ""


def test_tts():
    """Test basique TTS"""
    try:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text="Bonjour, ceci est un test.")
        voice = texttospeech.VoiceSelectionParams(
            language_code="fr-FR", name="fr-FR-Wavenet-A"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Sauvegarder le fichier test
        with open("test_tts.mp3", "wb") as f:
            f.write(response.audio_content)

        print("✅ TTS test: Audio généré (test_tts.mp3)")
        return True

    except Exception as e:
        print(f"❌ Erreur TTS: {e}")
        return False


def main(url):
    """Test complet simplifié"""
    print("🎵 Test du traducteur YouTube (version simplifiée)")
    print("=" * 60)

    # Test connexion
    if not test_basic_connectivity():
        return

    # Téléchargement
    audio_file, metadata = download_audio(url)

    # Transcription test
    text = transcribe_sample(audio_file)
    translated = ""

    # Traduction test
    if text:
        translated = translate_sample(text)

    # TTS test
    tts_ok = test_tts()

    # Nettoyage
    try:
        import os

        for file in ["audio_test.mp3", "audio_test.m4a", "audio_test.webm"]:
            if os.path.exists(file):
                os.remove(file)
        print("🧹 Fichiers de test nettoyés")
    except:
        pass

    print("\n" + "=" * 60)
    if text and translated and tts_ok:
        print("🎉 Test complet réussi ! Le traducteur fonctionne.")
        print("📊 Résumé :")
        print(f"   • Vidéo : {metadata['title']}")
        print(f"   • Durée : {metadata['duration']} secondes")
        print(f"   • Texte original : {text[:50]}...")
        print(f"   • Texte traduit : {translated[:50]}...")
        print("   • Audio TTS : Généré")
    else:
        print("⚠️ Test partiellement réussi - certains composants ont échoué")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_translation.py 'https://youtu.be/VIDEO_ID'")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
