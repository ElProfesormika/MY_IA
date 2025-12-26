#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration de l'API Hugging Face
"""

import requests
import config

def test_api_connection():
    """Teste la connexion à l'API Hugging Face"""
    
    print("🧪 Test de connexion à l'API Hugging Face\n")
    print(f"📍 URL utilisée: {config.HUGGINGFACE_API_URL}")
    print(f"🔑 Clé API: {config.HUGGINGFACE_API_KEY[:10]}...{config.HUGGINGFACE_API_KEY[-5:]}\n")
    
    headers = {
        "Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test avec un prompt simple
    payload = {
        "inputs": "Bonjour, peux-tu me dire bonjour en français?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    print("📤 Envoi de la requête...")
    
    try:
        response = requests.post(
            config.HUGGINGFACE_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📥 Code de réponse: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS ! L'API fonctionne correctement.\n")
            print("📝 Réponse reçue:")
            print("-" * 50)
            
            # Afficher la réponse selon le format
            if isinstance(result, list) and len(result) > 0:
                print(result[0].get('generated_text', result[0]))
            elif isinstance(result, dict):
                print(result.get('generated_text', result.get('text', result)))
            else:
                print(result)
            
            print("-" * 50)
            return True
            
        elif response.status_code == 401:
            print("❌ ERREUR 401: Clé API invalide ou expirée")
            print("   → Vérifiez votre clé API dans config.py")
            print("   → Allez sur https://huggingface.co/settings/tokens")
            return False
            
        elif response.status_code == 403:
            print("❌ ERREUR 403: Accès refusé")
            print("   → Vérifiez les permissions de votre token")
            return False
            
        elif response.status_code == 404:
            print("❌ ERREUR 404: Modèle non trouvé")
            print(f"   → Vérifiez que l'URL est correcte: {config.HUGGINGFACE_API_URL}")
            print("   → Essayez un autre modèle")
            return False
            
        elif response.status_code == 503:
            print("⏳ ERREUR 503: Modèle en cours de chargement")
            print("   → Attendez 10-30 secondes et réessayez")
            print("   → C'est normal pour les modèles gratuits")
            return False
            
        elif response.status_code == 410:
            print("❌ ERREUR 410: URL de l'API obsolète")
            print("   → L'URL a changé, utilisez router.huggingface.co")
            return False
            
        else:
            print(f"❌ ERREUR {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détails: {error_detail}")
            except:
                print(f"   Réponse: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: L'API prend trop de temps à répondre")
        print("   → Vérifiez votre connexion internet")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERREUR DE CONNEXION: {str(e)}")
        print("   → Vérifiez votre connexion internet")
        print("   → Vérifiez que l'URL est correcte")
        return False
        
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE: {str(e)}")
        return False

def test_alternative_urls():
    """Teste différentes URLs alternatives"""
    print("\n🔄 Test des URLs alternatives...\n")
    
    base_urls = [
        "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
    ]
    
    headers = {
        "Authorization": f"Bearer {config.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "test",
        "parameters": {"max_new_tokens": 10}
    }
    
    for url in base_urls:
        print(f"Test: {url}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 410:
                print(f"  ✅ Code {response.status_code} - Cette URL fonctionne!")
            else:
                print(f"  ❌ Code {response.status_code} - URL obsolète")
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)[:50]}")
        print()

if __name__ == "__main__":
    success = test_api_connection()
    
    if not success:
        print("\n" + "="*60)
        test_alternative_urls()
        print("="*60)
        print("\n💡 Conseils:")
        print("1. Vérifiez votre clé API sur https://huggingface.co/settings/tokens")
        print("2. Essayez de changer l'URL dans config.py")
        print("3. Consultez GUIDE_API.md pour plus d'aide")

