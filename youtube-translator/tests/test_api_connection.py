#!/usr/bin/env python3
"""
Tests minimalistes pour le traducteur YouTube
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour importer config
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import speech, translate_v2, texttospeech
from config import Config


def test_api_connection():
    """Test de connexion aux APIs Google Cloud"""
    print("🧪 Test de connexion Google Cloud APIs...")

    try:
        # Test Speech-to-Text
        speech_client = speech.SpeechClient()
        print("✅ Speech-to-Text: Connecté")

        # Test Translation
        translate_client = translate_v2.Client()
        result = translate_client.translate("Hello world", target_language="fr")
        if "Bonjour" in result.get("translatedText", ""):
            print("✅ Translation: Fonctionnel")
        else:
            print("⚠️ Translation: Réponse inattendue")
            return False

        # Test Text-to-Speech
        tts_client = texttospeech.TextToSpeechClient()
        print("✅ Text-to-Speech: Connecté")

        return True

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n🔧 Vérifiez:")
        print("- GOOGLE_APPLICATION_CREDENTIALS défini")
        print("- GOOGLE_CLOUD_PROJECT défini")
        print("- Clé JSON valide et permissions suffisantes")
        return False


def test_environment():
    """Test des variables d'environnement"""
    print("🧪 Test des variables d'environnement...")

    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not creds:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS non défini")
        return False
    if not Path(creds).exists():
        print(f"❌ Fichier de clés introuvable: {creds}")
        return False
    if not project:
        print("❌ GOOGLE_CLOUD_PROJECT non défini")
        return False

    print("✅ Variables d'environnement: OK")
    return True


def main():
    """Fonction principale des tests"""
    print("🧪 Suite de tests minimalistes")
    print("=" * 40)

    # Test environnement
    if not test_environment():
        return False

    # Test APIs
    if not test_api_connection():
        return False

    print("\n🎉 Tous les tests sont passés!")
    print("Le traducteur est prêt à fonctionner.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
