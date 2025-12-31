# Déploiement sur Vercel

## Configuration

Ce projet est configuré pour être déployé sur Vercel.

### Fichiers de configuration

- `vercel.json` : Configuration Vercel
- `api/index.py` : Point d'entrée pour Vercel
- `.vercelignore` : Fichiers à ignorer lors du déploiement

## Variables d'environnement à configurer sur Vercel

**Guide détaillé** : Consultez [GUIDE_CONFIGURATION_VERCEL.md](./GUIDE_CONFIGURATION_VERCEL.md) pour un guide pas à pas avec captures d'écran.

### Configuration Rapide :

Dans les paramètres de votre projet Vercel (Settings > Environment Variables), ajoutez ces variables :

#### 1. Clé API Mistral Principale (Obligatoire)
- **Nom** : `MISTRAL_API_KEY`
- **Valeur** : `jqm2diYfGA7sGqedt6Jj4e0uVWnheEAC`
- **Environnements** : Production, Preview, Development

#### 2. Clé API Mistral de Secours (Recommandé)
- **Nom** : `MISTRAL_API_KEY_BACKUP`
- **Valeur** : `u7JENkl50uqSrsZm8UZ432zDiWdkwbPT`
- **Environnements** : Production, Preview, Development
- **Important** : Utilisée automatiquement si la clé principale échoue

#### 3. Modèle Mistral (Optionnel)
- **Nom** : `MISTRAL_MODEL`
- **Valeur** : `mistral-small-latest`
- **Environnements** : Production, Preview, Development
- **Par défaut** : `mistral-small-latest` si non défini

### Étapes Détaillées :

1. Allez sur https://vercel.com et connectez-vous
2. Sélectionnez votre projet
3. Cliquez sur **Settings** → **Environment Variables**
4. Cliquez sur **Add New** pour chaque variable
5. Redéployez l'application (les variables ne sont chargées qu'au déploiement)

**Voir le guide complet** : [GUIDE_CONFIGURATION_VERCEL.md](./GUIDE_CONFIGURATION_VERCEL.md)

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

- **API Mistral uniquement** : L'application utilise exclusivement l'API Mistral (plus de Hugging Face)
- **Double clé API** : Système de fallback automatique entre clé principale et clé de secours
- **Cache désactivé** : Le cache est désactivé sur toutes les réponses pour garantir des données à jour
- **Traitement parallèle** : Les objectifs sont traités en parallèle (max 3 threads) pour plus de rapidité
- **Timeout optimisé** : Timeout API à 8 secondes pour compatibilité avec Vercel gratuit (limite 10s)
- **Logs détaillés** : Les logs Vercel affichent quelle clé API est utilisée et les erreurs éventuelles

## Dépannage - Erreur 500 sur Vercel

### Problème : "This Serverless Function has crashed" / 500: INTERNAL_SERVER_ERROR

**Solutions :**

1. **Vérifier les variables d'environnement sur Vercel** :
   - Allez dans votre projet Vercel > Settings > Environment Variables
   - Ajoutez toutes les variables nécessaires :
     - `MISTRAL_API_KEY` (obligatoire) - Votre clé API Mistral principale
     - `MISTRAL_API_KEY_BACKUP` (recommandé) - Votre clé API Mistral de secours
     - `MISTRAL_MODEL` (optionnel, défaut: `mistral-small-latest`)
   - **Important** : Les deux clés API Mistral sont recommandées pour la redondance

2. **Vérifier les logs de déploiement** :
   - Allez dans Deployments > Cliquez sur le dernier déploiement
   - Regardez les "Function Logs" pour voir l'erreur exacte
   - Les erreurs courantes sont :
     - `ModuleNotFoundError` : Vérifiez `requirements.txt`
     - `ImportError` : Vérifiez les chemins d'import
     - `AttributeError` : Vérifiez que les variables d'environnement sont définies

3. **Tester localement avec Vercel CLI** :
   ```bash
   npm i -g vercel
   vercel dev
   ```

4. **Vérifier la structure des fichiers** :
   - `api/index.py` doit exister et importer `app`
   - `app.py` doit être à la racine
   - `templates/` et `static/` doivent exister

5. **Redéployer après corrections** :
   ```bash
   git push  # Déclenchera un nouveau déploiement automatique
   ```

