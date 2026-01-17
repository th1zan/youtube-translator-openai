# Guide de configuration Google Cloud pour le Traducteur YouTube

## 📋 Checklist des étapes

- [ ] Créer/compte Google Cloud
- [ ] Créer un projet
- [ ] Activer les APIs nécessaires
- [ ] Créer un compte de service
- [ ] Générer la clé JSON
- [ ] Configurer l'environnement local
- [ ] Tester la connexion

## 🛠️ APIs à activer

### 1. Speech-to-Text API
- URL: https://console.cloud.google.com/apis/library/speech.googleapis.com
- Usage: Transcription audio avec diarization

### 2. Translation API
- URL: https://console.cloud.google.com/apis/library/translate.googleapis.com
- Usage: Traduction anglais → français

### 3. Text-to-Speech API
- URL: https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
- Usage: Génération audio avec voix premium

## 🔐 Création du compte de service

1. Aller dans "IAM & Admin" > "Comptes de service"
2. Cliquer "Créer un compte de service"
3. Nom: `youtube-translator`
4. Rôle: `Owner` (ou rôles spécifiques si vous préférez)

## 📥 Téléchargement de la clé

1. Dans le compte de service créé, onglet "Clés"
2. "Ajouter une clé" > "Créer une nouvelle clé" > JSON
3. Télécharger le fichier `youtube-translator-xxxxx.json`

## ⚙️ Configuration locale

```bash
# Se placer dans le répertoire du projet
cd youtube-translator

# Configurer les variables d'environnement
./setup_keys.sh /path/to/youtube-translator-xxxxx.json YOUR_PROJECT_ID

# Tester la connexion
uv run python tests/test_api_connection.py
```

## 🧪 Test rapide

Une fois configuré, testez avec une courte vidéo YouTube :

```bash
uv run python test_quick.py "https://youtu.be/dQw4w9WgXcQ"
```

## 💰 Crédits et coûts

- **Crédit gratuit** : 300$ pour les nouveaux comptes
- **Coût estimé** : ~1.62$ pour 1h de vidéo
- **APIs gratuites** : 60 minutes/mois pour Speech-to-Text

## 🔧 Dépannage

### Erreur "PERMISSION_DENIED"
- Vérifier que les APIs sont activées
- Vérifier les rôles du compte de service

### Erreur "QUOTA_EXCEEDED"
- Attendre la réinitialisation du quota (début de mois)
- Ou demander une augmentation de quota

### Erreur "INVALID_ARGUMENT"
- Vérifier le format de l'URL YouTube
- Vérifier que la vidéo est publique

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les variables d'environnement
2. Testez avec `./setup_keys.sh`
3. Lancez les tests unitaires
4. Consultez les logs détaillés