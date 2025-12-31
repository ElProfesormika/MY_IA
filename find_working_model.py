#!/usr/bin/env python3
"""
Script pour trouver un modèle Hugging Face qui fonctionne avec l'API gratuite
"""

import requests
import config

# Liste de modèles à tester (modèles généralement disponibles gratuitement)
MODELS_TO_TEST = [
    "google/flan-t5-large",
    "google/flan-t5-base",
    "microsoft/DialoGPT-medium",
    "microsoft/DialoGPT-large",
    "facebook/blenderbot-400M-distill",
    "distilgpt2",
    "gpt2",
    "EleutherAI/gpt-neo-125M",
    "t5-base",
    "t5-small",
]

BASE_URLS = [
    "https://router.huggingface.co/models",
    "https://api-inference.huggingface.co/models",
]

def test_model(base_url, model_name):
    """Teste si un modèle fonctionne"""
    url = f"{base_url}/{model_name}"
    headers = {
        "Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "Bonjour",
        "parameters": {
            "max_new_tokens": 20,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            return True, "FONCTIONNE"
        elif response.status_code == 503:
            return True, "En chargement (devrait fonctionner)"
        elif response.status_code == 401:
            return False, "Clé API invalide"
        elif response.status_code == 404:
            return False, "Modèle non trouvé"
        elif response.status_code == 410:
            return False, "URL obsolète"
        else:
            return False, f"Code {response.status_code}"
    except Exception as e:
        return False, f"Erreur: {str(e)[:30]}"

print("Recherche d'un modèle qui fonctionne avec l'API Hugging Face...\n")
print(f"Clé API: {config.HUGGINGFACE_API_KEY[:10]}...{config.HUGGINGFACE_API_KEY[-5:]}\n")
print("="*70)

working_models = []

for base_url in BASE_URLS:
    print(f"\nTest avec: {base_url}\n")
    
    for model in MODELS_TO_TEST:
        works, status = test_model(base_url, model)
        print(f"  {model:50} {status}")
        
        if works:
            full_url = f"{base_url}/{model}"
            working_models.append((full_url, model))
            print(f"     URL à utiliser: {full_url}")

print("\n" + "="*70)

if working_models:
    print("\nMODÈLES QUI FONCTIONNENT:\n")
    for url, model in working_models:
        print(f"  {model}")
        print(f"     URL: {url}\n")
    
    print("\nPour utiliser un de ces modèles, modifiez config.py:")
    print(f"   HUGGINGFACE_API_URL = \"{working_models[0][0]}\"")
else:
    print("\nAucun modèle gratuit trouvé.")
    print("\nSolutions possibles:")
    print("   1. Vérifiez votre clé API sur https://huggingface.co/settings/tokens")
    print("   2. Attendez quelques minutes et réessayez (certains modèles se chargent)")
    print("   3. Essayez d'utiliser l'API Mistral directement (payante)")
    print("   4. Utilisez un autre service d'IA gratuit comme OpenAI (avec clé API)")




