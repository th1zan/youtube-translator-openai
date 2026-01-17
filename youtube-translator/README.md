# Traducteur YouTube Audio

Traduit automatiquement les vidéos YouTube de l'anglais vers le français avec préservation des locuteurs distincts.

## Fonctionnalités

- 🎵 **Téléchargement audio** YouTube haute qualité
- 🗣️ **Diarization** : Séparation automatique des 2 locuteurs
- 🌐 **Traduction** : Anglais → Français avec Google Translate
- 🔊 **Voix premium** : Wavenet (qualité supérieure)
- ⏸️ **Pauses préservées** : Synchronisation temporelle maintenue
- 📋 **Métadonnées** : Tags ID3 complets

## Installation

```bash
# Installation de UV (si nécessaire)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialisation et dépendances
uv init youtube-translator
cd youtube-translator
uv add google-cloud-speech google-cloud-translate google-cloud-texttospeech yt-dlp pydub
```

## Configuration Google Cloud

1. **Créer un projet** : https://console.cloud.google.com/
2. **Activer les APIs** :
   - Speech-to-Text API
   - Translation API
   - Text-to-Speech API
3. **Créer une clé de service** :
   ```bash
   gcloud iam service-accounts create youtube-translator
   gcloud iam service-accounts keys create key.json --iam-account=youtube-translator@PROJECT_ID.iam.gserviceaccount.com
   ```
4. **Variables d'environnement** :
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

## Utilisation

### Version Simplifiée (recommandée pour tests)
```bash
# Test des APIs
uv run python tests/test_api_connection.py

# Traduction basique (sans diarization complète)
./translate.sh "https://youtu.be/VIDEO_ID"
```

### Version Complète (avec voix distinctes)
```bash
# Traduction complète avec diarization simulée et voix premium
./translate_complete.sh "https://youtu.be/VIDEO_ID"
```

## Sortie

- **Dossier** : `output/` (tous les fichiers générés)
- **Fichier MP3** avec voix distinctes (masculin/féminin)
- **Métadonnées ID3** : titre, auteur, durée originale
- **Format** : MP3 44.1kHz stéréo
- **Locuteurs** : Voix alternées selon la diarization

## Coûts (1h audio)

- Speech-to-Text : $1.44
- Translation : $0.05
- Text-to-Speech (Premium) : $0.13
- **Total** : **$1.62**

## Limites

- Vidéos YouTube publiques uniquement
- Transcription limitée à ~60 secondes (version actuelle)
- 2 locuteurs maximum (diarization simulée)
- Nécessite ffmpeg pour l'assemblage audio

## Améliorations futures

- **Diarization complète** : Intégration Google Cloud Storage pour fichiers longs
- **Segmentation automatique** : Découpage de vidéos longues
- **Optimisation coûts** : Cache des traductions fréquentes

## Dépannage

- **Erreur de connexion** : Vérifier les variables d'environnement
- **Quota dépassé** : Attendre ou augmenter les quotas Google Cloud
- **Audio trop long** : Le script gère automatiquement la segmentation