#!/bin/bash
# Script automatique de configuration Google Cloud pour le traducteur YouTube

set -e # Arrêt en cas d'erreur

echo "🚀 Configuration automatique Google Cloud pour le traducteur YouTube"
echo "=================================================================="

# Vérification de gcloud
if ! command -v gcloud &>/dev/null; then
	echo "❌ gcloud n'est pas installé. Installez d'abord Google Cloud CLI."
	exit 1
fi

# Connexion à Google Cloud (si nécessaire)
echo ""
echo "🔐 Connexion à Google Cloud..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
	echo "Aucun compte actif trouvé. Connexion interactive..."
	gcloud auth login
else
	echo "✅ Compte déjà connecté"
fi

# Choix ou création du projet
echo ""
echo "📁 Configuration du projet..."

# Lister les projets existants
echo "Projets disponibles :"
gcloud projects list --format="table(project_id, name, project_number)"

echo ""
read -p "Entrez l'ID du projet à utiliser (ou vide pour en créer un nouveau) : " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
	read -p "Nom du nouveau projet : " PROJECT_NAME
	PROJECT_ID=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g')

	echo "Création du projet '$PROJECT_NAME' avec ID '$PROJECT_ID'..."
	gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME"
fi

# Définir le projet actif
echo "Définition du projet actif : $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Activer les APIs nécessaires
echo ""
echo "🔌 Activation des APIs Google Cloud..."

APIs=(
	"speech.googleapis.com"       # Speech-to-Text
	"translate.googleapis.com"    # Translation
	"texttospeech.googleapis.com" # Text-to-Speech
)

for api in "${APIs[@]}"; do
	echo "Activation de $api..."
	gcloud services enable "$api"
done

echo "✅ APIs activées"

# Créer le compte de service
echo ""
echo "👤 Création du compte de service..."

SERVICE_ACCOUNT_NAME="youtube-translator"
SERVICE_ACCOUNT_ID="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Supprimer si existe déjà
gcloud iam service-accounts delete "$SERVICE_ACCOUNT_ID" --quiet 2>/dev/null || true

# Créer le compte
gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
	--description="Service account for YouTube audio translator" \
	--display-name="YouTube Translator"

echo "✅ Compte de service créé : $SERVICE_ACCOUNT_ID"

# Créer et télécharger la clé
echo ""
echo "🔑 Création de la clé d'authentification..."

KEY_FILE="${SERVICE_ACCOUNT_NAME}-key.json"

# Supprimer la clé existante si elle existe
if [ -f "$KEY_FILE" ]; then
	rm -f "$KEY_FILE"
fi

gcloud iam service-accounts keys create "$KEY_FILE" \
	--iam-account="$SERVICE_ACCOUNT_ID"

echo "✅ Clé créée : $KEY_FILE"

# Configuration des variables d'environnement
echo ""
echo "⚙️ Configuration des variables d'environnement..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat >.env <<EOF
# Configuration Google Cloud pour le traducteur YouTube
export GOOGLE_APPLICATION_CREDENTIALS="$SCRIPT_DIR/$KEY_FILE"
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
EOF

echo "✅ Fichier .env créé"

# Test des APIs
echo ""
echo "🧪 Test des APIs..."

python3 -c "
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '$SCRIPT_DIR/$KEY_FILE'
os.environ['GOOGLE_CLOUD_PROJECT'] = '$PROJECT_ID'

from google.cloud import speech, translate_v2, texttospeech

try:
    speech.SpeechClient()
    print('✅ Speech-to-Text: OK')
    translate_v2.Client()
    print('✅ Translation: OK')
    texttospeech.TextToSpeechClient()
    print('✅ Text-to-Speech: OK')
    print('🎉 Toutes les APIs fonctionnent!')
except Exception as e:
    print(f'❌ Erreur: {e}')
    exit(1)
"

echo ""
echo "🎊 Configuration terminée avec succès !"
echo ""
echo "📋 Récapitulatif :"
echo "   • Projet : $PROJECT_ID"
echo "   • Compte de service : $SERVICE_ACCOUNT_ID"
echo "   • Clé : $KEY_FILE"
echo ""
echo "🚀 Pour utiliser le traducteur :"
echo "   source .env  # Charger les variables"
echo "   uv run python translate_youtube.py 'https://youtu.be/VIDEO_ID'"
echo ""
echo "💡 Pensez à activer la facturation si nécessaire :"
echo "   https://console.cloud.google.com/billing/projects/$PROJECT_ID"
