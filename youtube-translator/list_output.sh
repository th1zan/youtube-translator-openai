#!/bin/bash
# Liste les fichiers traduits dans le dossier output

echo "📁 Fichiers traduits dans output/"
echo "================================"

# Chemin vers le dossier output (relatif au répertoire youtube-translator)
OUTPUT_DIR="../output"

if [ ! -d "$OUTPUT_DIR" ]; then
	echo "❌ Dossier output introuvable"
	exit 1
fi

# Compter les fichiers
count=$(ls -1 "$OUTPUT_DIR"/*traduit.mp3 2>/dev/null | wc -l)

if [ "$count" -eq 0 ]; then
	echo "📭 Aucun fichier traduit trouvé"
	echo ""
	echo "💡 Lancez une traduction avec :"
	echo "   ./translate_complete.sh 'https://youtu.be/VIDEO_ID'"
	exit 0
fi

echo "📊 $count fichier(s) trouvé(s) :"
echo ""

# Lister les fichiers avec détails
ls -lh "$OUTPUT_DIR"/*traduit.mp3 | while read line; do
	filename=$(echo "$line" | awk '{print $9}' | sed 's|.*/||')
	size=$(echo "$line" | awk '{print $5}')
	echo "🎵 $filename ($size)"
done

echo ""
echo "🎧 Pour écouter un fichier :"
echo "   afplay ../output/NOM_DU_FICHIER.mp3"
