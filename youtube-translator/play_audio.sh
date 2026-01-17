#!/bin/bash
# Ouvre le fichier MP3 généré

echo "🎵 Fichiers MP3 traduits disponibles :"
echo "====================================="

# Lister tous les fichiers traduits dans output
mp3_files=$(ls -1 output/*traduit.mp3 2>/dev/null)

if [ -z "$mp3_files" ]; then
	echo "❌ Aucun fichier MP3 trouvé"
	echo "Lancez d'abord une traduction avec ./translate_complete.sh"
	exit 1
fi

echo "$mp3_files"
echo ""
echo "📁 Chemin complet pour ouvrir dans votre lecteur audio :"
echo "$(pwd)/$mp3_files"
echo ""
echo "🌐 Ou via l'interface web OpenCode :"
echo "   Le dossier 'output' contient tous les fichiers traduits"
echo ""
echo "💡 Pour écouter :"
echo "   • Ouvrez votre lecteur audio préféré"
echo "   • Collez le chemin ci-dessus"
echo "   • OU utilisez la commande : afplay \"$mp3_files\""
