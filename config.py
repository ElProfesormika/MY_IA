"""
Configuration des APIs IA

RECOMMANDÉ : Utilisez l'API Mistral (gratuite et fonctionne bien en français)
ALTERNATIVE : Hugging Face (gratuite mais peut avoir des limitations)

IMPORTANT : Les clés API sont maintenant lues depuis les variables d'environnement
Créez un fichier .env avec vos clés API (voir .env.example)
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# ============================================
# 🔑 API MISTRAL (RECOMMANDÉ - GRATUITE)
# ============================================
# Pour obtenir votre clé API Mistral :
# 1. Allez sur https://console.mistral.ai/
# 2. Créez un compte (gratuit)
# 3. Allez dans "API Keys"
# 4. Créez une nouvelle clé
# 5. Copiez la clé dans le fichier .env

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")  # Lire depuis variable d'environnement

# Modèle Mistral à utiliser (gratuit)
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")  # ou "mistral-tiny-latest" pour plus rapide

# ============================================
# 🔑 API HUGGING FACE (ALTERNATIVE)
# ============================================
# Pour obtenir votre clé API Hugging Face :
# 1. Allez sur https://huggingface.co/settings/tokens
# 2. Créez un nouveau token (type: Read)
# 3. Copiez le token dans le fichier .env (commence par hf_)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# 🔗 URL DE L'API HUGGING FACE (si vous utilisez Hugging Face)
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL", "https://router.huggingface.co/models/google/flan-t5-base")

