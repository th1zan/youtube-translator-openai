#!/bin/bash
# Script pour pousser vers GitHub
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub

echo "🚀 Configuration du remote GitHub"
echo "=================================="

# Remplacer par votre repo GitHub
echo "📝 Commandes à exécuter :"
echo ""
echo "# 1. Ajouter le remote (remplacez VOTRE_USERNAME) :"
echo "git remote add origin https://github.com/VOTRE_USERNAME/youtube-translator-openai.git"
echo ""
echo "# 2. Pousser le code :"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "💡 Ou si vous voulez utiliser SSH :"
echo "git remote add origin git@github.com:VOTRE_USERNAME/youtube-translator-openai.git"
echo ""
echo "🔒 Pensez à configurer vos clés API localement après le clone !"
echo "   (Le fichier google-cloud-key.json n'est pas committé pour sécurité)"
