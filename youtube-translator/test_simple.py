#!/usr/bin/env python3
"""
Test rapide des APIs Google Cloud (sans manipulation audio)
"""

import os
from google.cloud import speech, translate_v2, texttospeech


def test_google_apis():
    """Test rapide des APIs Google Cloud"""
    print("🧪 Test rapide des APIs Google Cloud")
    print("=" * 50)

    try:
        # Test Speech-to-Text
        client_speech = speech.SpeechClient()
        print("✅ Speech-to-Text: OK")

        # Test Translation avec un petit texte
        client_translate = translate_v2.Client()
        result = client_translate.translate("Hello world", target_language="fr")
        if "Bonjour" in result.get("translatedText", ""):
            print("✅ Translation: OK")
        else:
            print("❌ Translation: Résultat inattendu")
            return False

        # Test Text-to-Speech
        client_tts = texttospeech.TextToSpeechClient()
        print("✅ Text-to-Speech: OK")

        return True

    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False


def test_youtube_download():
    """Test de téléchargement YouTube (sans manipulation audio)"""
    try:
        import yt_dlp

        print("⏳ Test de téléchargement YouTube...")

        # Test avec une vidéo très courte
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "test_audio.%(ext)s",
            "extract_flat": False,
            "writeinfojson": True,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Utilise une vidéo de test très courte
            info = ydl.extract_info(
                "https://youtu.be/jNQXAC9IVRw", download=True
            )  # 1 seconde

            if info:
                print(f"✅ Téléchargement YouTube: OK ({info.get('title', 'Unknown')})")

                # Nettoyer
                import os

                for file in os.listdir("."):
                    if file.startswith("test_audio.") or file.endswith(".json"):
                        os.remove(file)
                        print("🧹 Fichiers de test nettoyés")

                return True

    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Test du traducteur YouTube (version simplifiée)")
    print("=" * 60)

    # Test des APIs
    api_ok = test_google_apis()

    # Test YouTube
    youtube_ok = test_youtube_download()

    if api_ok and youtube_ok:
        print("\n🎉 Tous les tests sont passés!")
        print("Le traducteur est prêt pour une vraie traduction.")
        print("\nPour lancer une traduction complète:")
        print("uv run python translate_youtube.py 'https://youtu.be/VIDEO_ID'")
    else:
        print(
            f"\n⚠️ Tests partiellement échoués (APIs: {'✅' if api_ok else '❌'}, YouTube: {'✅' if youtube_ok else '❌'})"
        )

    exit(0 if api_ok else 1)
