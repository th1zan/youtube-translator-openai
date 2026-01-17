#!/bin/bash
# Script pour partager les fichiers MP3 générés
# Utilise OpenCode /share ou exporte vers un dossier partagé

echo "📁 Partage des fichiers MP3 générés"
echo "==================================="

# Vérifier s'il y a des fichiers MP3
mp3_count=$(ls -1 output/*.mp3 2>/dev/null | wc -l)

if [ "$mp3_count" -eq 0 ]; then
	echo "❌ Aucun fichier MP3 trouvé dans output/"
	echo "Générez d'abord une traduction avec ./translate_complete.sh"
	exit 1
fi

echo "📊 $mp3_count fichier(s) MP3 trouvé(s) :"
ls -lh output/*.mp3
echo ""

echo "🔗 Options de partage :"
echo ""
echo "1️⃣ Via OpenCode (recommandé) :"
echo "   • Tapez '/share' dans le chat OpenCode"
echo "   • Sélectionnez le dossier output/"
echo "   • Partagez le lien généré"
echo ""
echo "2️⃣ Via dossier partagé :"
echo "   • cp -r output/ ~/Desktop/Partage_Traduction/"
echo "   • Partagez le dossier ~/Desktop/Partage_Traduction/"
echo ""
echo "3️⃣ Via cloud (optionnel) :"
echo "   • Upload vers Google Drive, Dropbox, etc."
echo "   • rclone copy output/ gdrive:Traduction_YouTube/"
echo ""
echo "🎵 Les fichiers restent disponibles localement dans output/"
