#!/usr/bin/env python3
"""
Test de l'API Mistral
"""

import requests
import config

print("Test de l'API Mistral\n")

if not config.MISTRAL_API_KEY or config.MISTRAL_API_KEY.strip() == "":
    print("Clé API Mistral non configurée dans config.py")
    exit(1)

print(f"Clé API: {config.MISTRAL_API_KEY[:10]}...{config.MISTRAL_API_KEY[-5:]}")
print(f"Modèle: {config.MISTRAL_MODEL}\n")

url = "https://api.mistral.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.MISTRAL_API_KEY}"
}

payload = {
    "model": config.MISTRAL_MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Dis-moi bonjour en français en une phrase."
        }
    ],
    "temperature": 0.7,
    "max_tokens": 50
}

print("Envoi de la requête...")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"Code de réponse: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('choices') and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            print("SUCCÈS ! L'API Mistral fonctionne parfaitement !\n")
            print("Réponse de l'IA:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            print("\nVotre application est prête à utiliser l'IA !")
        else:
            print("Réponse inattendue de l'API")
            print(result)
    elif response.status_code == 401:
        print("ERREUR 401: Clé API invalide")
        print("   Verifiez votre clé API dans config.py")
        print("   Allez sur https://console.mistral.ai/ pour verifier votre clé")
    elif response.status_code == 429:
        print("ERREUR 429: Quota dépassé")
        print("   Attendez quelques minutes ou verifiez votre quota")
    else:
        print(f"ERREUR {response.status_code}")
        try:
            error = response.json()
            print(f"   Détails: {error}")
        except:
            print(f"   Réponse: {response.text[:200]}")
            
except requests.exceptions.Timeout:
    print("TIMEOUT: L'API prend trop de temps à répondre")
except requests.exceptions.RequestException as e:
    print(f"ERREUR DE CONNEXION: {str(e)}")
except Exception as e:
    print(f"ERREUR INATTENDUE: {str(e)}")




