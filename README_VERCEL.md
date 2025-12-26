# Déploiement sur Vercel

## Configuration

Ce projet est configuré pour être déployé sur Vercel.

### Fichiers de configuration

- `vercel.json` : Configuration Vercel
- `api/index.py` : Point d'entrée pour Vercel
- `.vercelignore` : Fichiers à ignorer lors du déploiement

## Variables d'environnement à configurer sur Vercel

Dans les paramètres de votre projet Vercel, ajoutez ces variables d'environnement :

1. **MISTRAL_API_KEY** : Votre clé API Mistral
2. **MISTRAL_MODEL** : Le modèle Mistral à utiliser (ex: `mistral-small-latest`)
3. **HUGGINGFACE_API_KEY** : Votre clé API Hugging Face (optionnel, en fallback)
4. **HUGGINGFACE_API_URL** : URL de l'API Hugging Face (optionnel)

## Déploiement

1. Installez Vercel CLI : `npm i -g vercel`
2. Connectez-vous : `vercel login`
3. Déployez : `vercel`
4. Pour la production : `vercel --prod`

## Structure

```
/
├── app.py              # Application Flask principale
├── api/
│   └── index.py        # Point d'entrée pour Vercel
├── templates/          # Templates HTML
├── static/             # Fichiers statiques (CSS, JS, images)
├── config.py           # Configuration des APIs
├── vercel.json         # Configuration Vercel
└── requirements.txt    # Dépendances Python
```

## Notes

- Le cache est désactivé sur toutes les réponses pour garantir des données à jour
- Le traitement des objectifs est optimisé avec traitement parallèle (max 3 threads)
- Les timeouts API sont optimisés à 20 secondes pour une meilleure rapidité

