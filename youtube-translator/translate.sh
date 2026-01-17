#!/bin/bash
# Lanceur rapide pour le traducteur YouTube

set -e

# Configuration automatique des variables d'environnement
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GOOGLE_APPLICATION_CREDENTIALS="$SCRIPT_DIR/google-cloud-key.json"
export GOOGLE_CLOUD_PROJECT="yt-translate-484622"

echo "🔧 Variables d'environnement configurées"
echo "   GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
echo "   GOOGLE_CLOUD_PROJECT: $GOOGLE_CLOUD_PROJECT"
echo ""

# Vérification rapide des APIs
echo "🧪 Vérification rapide des APIs..."
if ! uv run python -c "
from google.cloud import speech, translate_v2, texttospeech
speech.SpeechClient()
translate_v2.Client()
texttospeech.TextToSpeechClient()
print('✅ APIs Google Cloud opérationnelles')
"; then
	echo "❌ Problème avec les APIs Google Cloud"
	exit 1
fi

echo ""

# Lancement du traducteur
if [ $# -eq 0 ]; then
	echo "Usage: $0 'https://youtu.be/VIDEO_ID'"
	echo "Exemple: $0 'https://youtu.be/dQw4w9WgXcQ'"
	exit 1
fi

URL="$1"
echo "🎵 Lancement de la traduction..."
echo "   URL: $URL"
echo ""

uv run python translate_youtube.py "$URL"
