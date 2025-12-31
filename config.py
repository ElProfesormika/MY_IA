"""
Configuration des APIs IA - Mistral uniquement

IMPORTANT : Les clés API sont lues depuis les variables d'environnement
Créez un fichier .env avec vos clés API (voir .env.example)
"""

import os

# Charger les variables d'environnement depuis .env (si le fichier existe)
# Sur Vercel, les variables d'environnement sont configurées directement
try:
    from dotenv import load_dotenv
    # Ne pas faire planter l'app si .env n'existe pas (normal sur Vercel)
    load_dotenv()
except (ImportError, Exception):
    # Si dotenv n'est pas disponible ou si .env n'existe pas, continuer quand même
    # Les variables d'environnement seront lues depuis os.getenv() directement
    pass

# ============================================
# API MISTRAL (PRINCIPALE ET SECOURS)
# ============================================
# Pour obtenir vos clés API Mistral :
# 1. Allez sur https://console.mistral.ai/
# 2. Créez un compte (gratuit)
# 3. Allez dans "API Keys"
# 4. Créez des clés API
# 5. Copiez les clés dans le fichier .env

# Clé API Mistral principale
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# Clé API Mistral de secours (utilisée si la principale échoue)
MISTRAL_API_KEY_BACKUP = os.getenv("MISTRAL_API_KEY_BACKUP", "")

# Modèle Mistral à utiliser (gratuit)
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")  # ou "mistral-tiny-latest" pour plus rapide

