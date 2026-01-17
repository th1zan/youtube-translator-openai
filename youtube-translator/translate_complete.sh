#!/bin/bash
# Lanceur pour la version complète du traducteur YouTube

set -e

# Configuration automatique des variables d'environnement
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GOOGLE_APPLICATION_CREDENTIALS="$SCRIPT_DIR/google-cloud-key.json"
export GOOGLE_CLOUD_PROJECT="yt-translate-484622"

echo "🔧 Variables d'environnement configurées"
echo "   GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
echo "   GOOGLE_CLOUD_PROJECT: $GOOGLE_CLOUD_PROJECT"
echo ""

# Test des APIs
echo "🧪 Test rapide des APIs..."
if ! uv run python -c "
from google.cloud import speech, translate_v2, texttospeech
speech.SpeechClient()
translate_v2.Client()
texttospeech.TextToSpeechClient()
print('✅ APIs opérationnelles')
" 2>/dev/null; then
	echo "❌ Problème avec les APIs Google Cloud"
	exit 1
fi

echo ""

# Lancement du traducteur complet
if [ $# -eq 0 ]; then
	echo "Usage: $0 'https://youtu.be/VIDEO_ID'"
	echo "Exemple: $0 'https://youtu.be/dQw4w9WgXcQ'"
	echo ""
	echo "📋 Version complète avec :"
	echo "   • Téléchargement YouTube"
	echo "   • Transcription avec diarization simulée"
	echo "   • Traduction anglais → français"
	echo "   • Voix premium Wavenet (locuteurs distincts)"
	echo "   • Assemblage MP3 final avec métadonnées"
	exit 1
fi

URL="$1"
echo "🎵 Lancement de la traduction complète..."
echo "   URL: $URL"
echo "   Sortie: MP3 avec voix distinctes (masculin/féminin)"
echo ""

uv run python translate_youtube_complete.py "$URL"
