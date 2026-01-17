#!/bin/bash
# Script de configuration des clés Google Cloud
# Usage: ./setup_keys.sh /path/to/service-account-key.json YOUR_PROJECT_ID

if [ $# -ne 2 ]; then
	echo "Usage: $0 <path-to-service-account-key.json> <project-id>"
	echo "Exemple: $0 ~/Downloads/youtube-translator-key.json my-project-12345"
	exit 1
fi

KEY_FILE="$1"
PROJECT_ID="$2"

if [ ! -f "$KEY_FILE" ]; then
	echo "❌ Fichier de clé introuvable: $KEY_FILE"
	exit 1
fi

# Exporter les variables
export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE"
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"

echo "✅ Variables d'environnement configurées:"
echo "   GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
echo "   GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
echo ""
echo "🔧 Pour les rendre permanentes, ajoutez ces lignes à votre ~/.bashrc ou ~/.zshrc:"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE\""
echo "   export GOOGLE_CLOUD_PROJECT=\"$PROJECT_ID\""
