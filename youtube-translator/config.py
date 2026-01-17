import os


class Config:
    # Google Cloud
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

    # Voix premium Google Wavenet
    VOICES = {
        1: "fr-FR-Wavenet-A",  # Masculin premium
        2: "fr-FR-Wavenet-E",  # Féminin premium
    }

    # Paramètres audio
    MIN_SILENCE_MS = 200  # Pause minimale conservée (ms)
    AUDIO_FORMAT = "mp3"
    SAMPLE_RATE = 44100

    # Timeouts et limites
    API_TIMEOUT = 300  # 5 minutes pour les longues opérations
    MAX_AUDIO_SIZE_MB = 10  # Limite Google Cloud
