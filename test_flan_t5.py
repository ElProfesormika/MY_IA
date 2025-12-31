#!/usr/bin/env python3
"""
Test spécifique pour google/flan-t5-base avec différentes URLs et formats
"""

import requests
import config

API_KEY = config.HUGGINGFACE_API_KEY
MODEL = "google/flan-t5-base"

# Différentes URLs à tester
URLS_TO_TEST = [
    f"https://router.huggingface.co/models/{MODEL}",
    f"https://api-inference.huggingface.co/models/{MODEL}",
    f"https://huggingface.co/api/models/{MODEL}",
]

# Différents formats de payload
PAYLOADS_TO_TEST = [
    # Format standard
    {
        "inputs": "Bonjour, comment allez-vous?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7,
            "return_full_text": False
        }
    },
    # Format simple
    {
        "inputs": "Bonjour, comment allez-vous?",
    },
    # Format avec options minimales
    {
        "inputs": "Bonjour",
        "parameters": {
            "max_length": 50
        }
    },
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"Test approfondi pour {MODEL}\n")
print(f"Clé API: {API_KEY[:10]}...{API_KEY[-5:]}\n")
print("="*70)

for url in URLS_TO_TEST:
    print(f"\nTest URL: {url}\n")
    
    for i, payload in enumerate(PAYLOADS_TO_TEST, 1):
        print(f"  Format {i}: ", end="")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            print(f"Code {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"     SUCCÈS!")
                print(f"     Réponse: {str(result)[:100]}...")
                print(f"\n     URL QUI FONCTIONNE: {url}")
                print(f"     Payload qui fonctionne:")
                import json
                print(f"     {json.dumps(payload, indent=6)}")
                break
            elif response.status_code == 503:
                print(f"     Modèle en chargement (devrait fonctionner après)")
            elif response.status_code == 401:
                print(f"     Clé API invalide")
                break
            elif response.status_code == 410:
                print(f"     URL obsolète")
                break
            elif response.status_code == 404:
                print(f"     Modèle non trouvé")
            else:
                try:
                    error = response.json()
                    print(f"     Erreur: {str(error)[:80]}")
                except:
                    print(f"     Erreur: {response.text[:80]}")
                    
        except requests.exceptions.Timeout:
            print(f"     Timeout")
        except Exception as e:
            print(f"     Exception: {str(e)[:50]}")
    
    print()

print("="*70)
print("\nSi aucun test n'a fonctionné:")
print("   1. Le modèle peut nécessiter un accès spécial")
print("   2. L'API gratuite peut avoir des limitations")
print("   3. Essayez un autre modèle ou une autre API (voir SOLUTIONS_API.md)")




