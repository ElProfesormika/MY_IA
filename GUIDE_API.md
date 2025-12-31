# Guide pour obtenir votre Clé API Hugging Face

## Étape 1 : Créer/Connecter votre compte Hugging Face

1. Allez sur **https://huggingface.co**
2. Cliquez sur **"Sign Up"** (ou **"S'inscrire"**) en haut à droite
3. Créez votre compte ou connectez-vous si vous en avez déjà un

## Étape 2 : Générer votre Clé API (Access Token)

1. Une fois connecté, cliquez sur votre **avatar** en haut à droite
2. Sélectionnez **"Settings"** (Paramètres)
3. Dans le menu de gauche, cliquez sur **"Access Tokens"** (Jetons d'accès)
4. Cliquez sur **"New token"** (Nouveau jeton)
5. Donnez un nom à votre jeton (ex: `mon-assistant-objectifs`)
6. Sélectionnez le niveau d'accès : **"Read"** (Lecture) suffit pour utiliser les modèles
7. Cliquez sur **"Generate token"** (Générer le jeton)
8. **IMPORTANT** : Copiez immédiatement votre jeton ! Il ne s'affichera qu'une seule fois.
   - Format : `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Étape 3 : Vérifier l'URL de l'API

L'URL de l'API dépend du modèle que vous voulez utiliser. Voici les options :

### Option 1 : Router API (Nouvelle API - Recommandée)
```
https://router.huggingface.co/models/[NOM_DU_MODELE]
```

### Option 2 : Inference API (Alternative)
```
https://api-inference.huggingface.co/models/[NOM_DU_MODELE]
```

### Modèles recommandés pour le français :
- `mistralai/Mistral-7B-Instruct-v0.2` (actuellement utilisé)
- `meta-llama/Llama-2-7b-chat-hf`
- `google/flan-t5-large`
- `microsoft/DialoGPT-large`

## Étape 4 : Configurer votre application

1. Ouvrez le fichier `config.py`
2. Remplacez `HUGGINGFACE_API_KEY` par votre clé API
3. Vérifiez que `HUGGINGFACE_API_URL` pointe vers le bon modèle

Exemple :
```python
HUGGINGFACE_API_KEY = "hf_VOTRE_CLE_ICI"
HUGGINGFACE_API_URL = "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
```

## Étape 5 : Tester votre configuration

Utilisez le script `test_api.py` pour vérifier que tout fonctionne :

```bash
python3 test_api.py
```

## ❓ Problèmes courants

### Erreur 401 (Unauthorized)
- Votre clé API est incorrecte ou expirée
- Vérifiez que vous avez bien copié la clé complète (commence par `hf_`)

### Erreur 503 (Service Unavailable)
- Le modèle est en cours de chargement
- Attendez 10-30 secondes et réessayez

### Erreur 410 (Gone)
- L'URL de l'API a changé
- Utilisez `router.huggingface.co` au lieu de `api-inference.huggingface.co`

### Erreur 429 (Too Many Requests)
- Vous avez dépassé la limite de requêtes gratuites
- Attendez quelques minutes ou passez à un compte payant

## Sécurité

**NE PARTAGEZ JAMAIS** votre clé API publiquement :
- Ne la commitez pas sur GitHub
- Ne la partagez pas dans des forums
- Utilisez un fichier `.env` ou `config.py` (qui devrait être dans `.gitignore`)

## Ressources

- Documentation officielle : https://huggingface.co/docs/api-inference
- Créer un token : https://huggingface.co/settings/tokens
- Liste des modèles : https://huggingface.co/models




