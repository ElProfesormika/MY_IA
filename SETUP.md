# Configuration et Déploiement

## Configuration des Clés API

### Étape 1 : Créer le fichier .env

Copiez le fichier `.env.example` en `.env` :

```bash
cp .env.example .env
```

### Étape 2 : Remplir vos clés API

Ouvrez le fichier `.env` et remplissez vos clés API :

```env
# API Mistral (Recommandé)
MISTRAL_API_KEY=votre_cle_mistral_ici
MISTRAL_MODEL=mistral-small-latest

# API Hugging Face (Alternative)
HUGGINGFACE_API_KEY=votre_cle_huggingface_ici
HUGGINGFACE_API_URL=https://router.huggingface.co/models/google/flan-t5-base
```

### Étape 3 : Obtenir vos clés API

#### Clé API Mistral (Recommandé)
1. Allez sur https://console.mistral.ai/
2. Créez un compte (gratuit)
3. Allez dans "API Keys"
4. Créez une nouvelle clé
5. Copiez la clé dans votre fichier `.env`

#### Clé API Hugging Face (Alternative)
1. Allez sur https://huggingface.co/settings/tokens
2. Créez un nouveau token (type: Read)
3. Copiez le token dans votre fichier `.env`

## Déploiement sur Vercel

### Variables d'environnement sur Vercel

Dans les paramètres de votre projet Vercel, ajoutez ces variables d'environnement :

1. **MISTRAL_API_KEY** : Votre clé API Mistral
2. **MISTRAL_MODEL** : Le modèle Mistral (ex: `mistral-small-latest`)
3. **HUGGINGFACE_API_KEY** : Votre clé API Hugging Face (optionnel)
4. **HUGGINGFACE_API_URL** : URL de l'API Hugging Face (optionnel)

## Push vers GitHub

Les secrets ont été retirés du code. Pour pousser vers GitHub :

```bash
# Vérifier que config.py ne contient plus de secrets
git diff HEAD~1 config.py

# Pousser vers GitHub
git push -u origin main
```

Si GitHub demande des identifiants, utilisez un token d'accès personnel :
1. Allez sur https://github.com/settings/tokens
2. Créez un nouveau token (classic) avec les permissions `repo`
3. Utilisez ce token comme mot de passe lors du push




