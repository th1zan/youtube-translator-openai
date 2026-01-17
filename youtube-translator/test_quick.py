#!/usr/bin/env python3
"""
Test rapide du traducteur YouTube
Utilisation: uv run python test_quick.py "URL_YOUTUBE"
"""

import sys
import os
from translate_youtube import test_basic_connectivity, download_audio


def test_quick(url):
    """Test rapide avec une vraie URL YouTube"""
    print("🧪 Test rapide du traducteur YouTube")
    print("=" * 50)

    # Test de connexion
    if not test_basic_connectivity():
        print("❌ Échec des tests de connexion")
        return False

    # Test de téléchargement
    try:
        print("\n📥 Test de téléchargement audio...")
        audio_file, metadata = download_audio(url)
        print(f"✅ Téléchargement réussi: {metadata['title']}")
        print(f"   Durée: {metadata['duration']} secondes")
        print(f"   Auteur: {metadata['uploader']}")

        # Nettoyer
        import os

        if os.path.exists(audio_file):
            os.remove(audio_file)
            print("🧹 Fichier temporaire nettoyé")

        return True

    except Exception as e:
        print(f"❌ Erreur de téléchargement: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python test_quick.py 'https://youtu.be/VIDEO_ID'")
        print("Exemple: uv run python test_quick.py 'https://youtu.be/dQw4w9WgXcQ'")
        sys.exit(1)

    url = sys.argv[1]
    success = test_quick(url)
    print(f"\n{'🎉 Test réussi!' if success else '❌ Test échoué'}")
    sys.exit(0 if success else 1)
