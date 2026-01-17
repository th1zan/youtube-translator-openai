#!/bin/bash
# Démonstration rapide du traducteur YouTube

echo "🎬 Démonstration du Traducteur YouTube"
echo "======================================"
echo ""

# Vidéo de démonstration (courte interview)
DEMO_URL="https://www.youtube.com/watch?v=LjIi5lDb1xo"
DEMO_TITLE="Interview d'embauche B1/B2 (3 minutes)"

echo "📹 Vidéo de démonstration:"
echo "   Titre: $DEMO_TITLE"
echo "   URL: $DEMO_URL"
echo ""

echo "🔧 Lancement de la traduction complète..."
echo "   • Téléchargement YouTube"
echo "   • Transcription anglaise"
echo "   • Traduction française"
echo "   • Synthèse vocale premium"
echo "   • Assemblage MP3 final"
echo ""

# Lancer la traduction
./translate_complete.sh "$DEMO_URL"

echo ""
echo "✅ Démonstration terminée!"
echo "   Vérifiez le fichier MP3 généré dans ce répertoire."
