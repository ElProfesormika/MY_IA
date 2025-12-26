# 🔧 Guide de Configuration des Variables d'Environnement sur Vercel

## 📋 Configuration des Clés API Mistral

Ce guide vous explique comment configurer les clés API Mistral sur Vercel pour que votre application fonctionne correctement.

---

## 🚀 Étapes de Configuration

### Étape 1 : Accéder aux Paramètres du Projet

1. Connectez-vous à votre compte Vercel : https://vercel.com
2. Sélectionnez votre projet (BuildNovaG_objectifs-AI)
3. Cliquez sur **Settings** (Paramètres) dans le menu de navigation
4. Dans le menu latéral, cliquez sur **Environment Variables** (Variables d'environnement)

### Étape 2 : Ajouter la Clé API Mistral Principale

1. Cliquez sur le bouton **Add New** (Ajouter nouveau)
2. Remplissez les champs :
   - **Name** (Nom) : `MISTRAL_API_KEY`
   - **Value** (Valeur) : `jqm2diYfGA7sGqedt6Jj4e0uVWnheEAC`
   - **Environment** : Cochez toutes les cases :
     - ✅ Production
     - ✅ Preview
     - ✅ Development
3. Cliquez sur **Save** (Enregistrer)

### Étape 3 : Ajouter la Clé API Mistral de Secours (Recommandé)

1. Cliquez à nouveau sur **Add New** (Ajouter nouveau)
2. Remplissez les champs :
   - **Name** (Nom) : `MISTRAL_API_KEY_BACKUP`
   - **Value** (Valeur) : `u7JENkl50uqSrsZm8UZ432zDiWdkwbPT`
   - **Environment** : Cochez toutes les cases :
     - ✅ Production
     - ✅ Preview
     - ✅ Development
3. Cliquez sur **Save** (Enregistrer)

### Étape 4 : Ajouter le Modèle Mistral (Optionnel)

1. Cliquez sur **Add New** (Ajouter nouveau)
2. Remplissez les champs :
   - **Name** (Nom) : `MISTRAL_MODEL`
   - **Value** (Valeur) : `mistral-small-latest`
   - **Environment** : Cochez toutes les cases :
     - ✅ Production
     - ✅ Preview
     - ✅ Development
3. Cliquez sur **Save** (Enregistrer)

> **Note** : Si vous ne définissez pas `MISTRAL_MODEL`, l'application utilisera `mistral-small-latest` par défaut.

---

## ✅ Vérification de la Configuration

### Vérifier dans l'Interface Vercel

Après avoir ajouté les variables, vous devriez voir dans la liste :

```
✅ MISTRAL_API_KEY          [Production, Preview, Development]
✅ MISTRAL_API_KEY_BACKUP   [Production, Preview, Development]
✅ MISTRAL_MODEL            [Production, Preview, Development] (optionnel)
```

### Vérifier dans les Logs de Déploiement

1. Allez dans **Deployments** (Déploiements)
2. Cliquez sur le dernier déploiement
3. Ouvrez **Function Logs** (Logs de fonction)
4. Vous devriez voir ces messages :

```
✅ Configuration Mistral : Clé principale détectée (modèle: mistral-small-latest)
   Clé principale (aperçu): jqm2diYfGA7sGq...
✅ Configuration Mistral : Clé de secours détectée
   Clé de secours (aperçu): u7JENkl50uqSrsZ...
```

---

## 🔄 Redéploiement après Configuration

### Option 1 : Redéploiement Automatique

Si vous avez connecté votre dépôt GitHub, Vercel redéploiera automatiquement après chaque push. Pour forcer un redéploiement :

1. Allez dans **Deployments**
2. Cliquez sur les **3 points** (⋯) du dernier déploiement
3. Sélectionnez **Redeploy** (Redéployer)

### Option 2 : Redéploiement via Git

```bash
# Faire un petit changement pour déclencher un redéploiement
git commit --allow-empty -m "Trigger redeploy after env vars config"
git push
```

---

## 🛠️ Dépannage

### Problème : Les variables ne sont pas détectées

**Solution 1 : Vérifier l'environnement**
- Assurez-vous que les variables sont configurées pour **Production**, **Preview** ET **Development**

**Solution 2 : Redéployer**
- Les variables d'environnement ne sont chargées qu'au moment du déploiement
- Redéployez votre application après avoir ajouté les variables

**Solution 3 : Vérifier les noms**
- Les noms doivent être **exactement** :
  - `MISTRAL_API_KEY` (pas `mistral_api_key` ou `Mistral_Api_Key`)
  - `MISTRAL_API_KEY_BACKUP` (pas `MISTRAL_API_KEY_BACKUP_` avec un underscore en plus)

### Problème : Erreur "Clé API invalide"

**Solution :**
1. Vérifiez que vous avez copié la clé complète (sans espaces avant/après)
2. Vérifiez que la clé est toujours valide sur https://console.mistral.ai/
3. Si nécessaire, créez une nouvelle clé API et mettez à jour la variable

### Problème : Timeout ou erreur 429

**Solution :**
- L'erreur 429 signifie que vous avez atteint la limite de taux
- La clé de secours sera automatiquement utilisée
- Attendez quelques minutes avant de réessayer

---

## 📝 Résumé des Variables Requises

| Variable | Obligatoire | Valeur Exemple | Description |
|----------|-------------|----------------|-------------|
| `MISTRAL_API_KEY` | ✅ Oui | `jqm2diYfGA7sGqedt6Jj4e0uVWnheEAC` | Clé API Mistral principale |
| `MISTRAL_API_KEY_BACKUP` | ⭐ Recommandé | `u7JENkl50uqSrsZm8UZ432zDiWdkwbPT` | Clé API Mistral de secours |
| `MISTRAL_MODEL` | ❌ Optionnel | `mistral-small-latest` | Modèle Mistral à utiliser |

---

## 🎯 Après Configuration

Une fois les variables configurées et l'application redéployée :

1. ✅ L'application utilisera automatiquement l'API Mistral
2. ✅ Si la clé principale échoue, la clé de secours sera utilisée automatiquement
3. ✅ Les logs Vercel afficheront quelle clé est utilisée
4. ✅ L'analyse IA fonctionnera pour les objectifs SMART et IKIGAI

---

## 🔗 Liens Utiles

- **Console Mistral** : https://console.mistral.ai/
- **Documentation Vercel** : https://vercel.com/docs/environment-variables
- **Documentation Mistral API** : https://docs.mistral.ai/

---

## 💡 Astuce

Pour tester rapidement si les variables sont bien configurées, vous pouvez créer une route de test temporaire dans `app.py` :

```python
@app.route('/test-env')
def test_env():
    return jsonify({
        "MISTRAL_API_KEY": "✅ Configurée" if MISTRAL_API_KEY else "❌ Non configurée",
        "MISTRAL_API_KEY_BACKUP": "✅ Configurée" if MISTRAL_API_KEY_BACKUP else "❌ Non configurée",
        "MISTRAL_MODEL": MISTRAL_MODEL
    })
```

⚠️ **N'oubliez pas de supprimer cette route en production !**

