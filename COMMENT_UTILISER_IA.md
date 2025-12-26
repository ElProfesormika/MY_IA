# 🎯 Comment Utiliser l'IA dans l'Application

## 🚀 Solution Simple : API Mistral (GRATUITE)

### ⚡ Étapes Rapides (5 minutes)

1. **Obtenez votre clé API Mistral** :
   - Allez sur https://console.mistral.ai/
   - Créez un compte (gratuit)
   - Allez dans "API Keys" → "Create API Key"
   - Copiez votre clé

2. **Configurez votre application** :
   - Ouvrez `config.py`
   - Trouvez : `MISTRAL_API_KEY = ""`
   - Collez votre clé : `MISTRAL_API_KEY = "votre_cle_ici"`
   - Sauvegardez

3. **Lancez l'application** :
   ```bash
   python3 app.py
   ```

4. **C'est prêt !** 🎉
   - Ouvrez http://localhost:5000
   - Remplissez les formulaires
   - Cliquez sur "Analyser avec l'IA"
   - L'IA fonctionnera automatiquement !

## 📋 Détails

### Fichier à Modifier : `config.py`

```python
# Trouvez cette ligne (ligne ~16) :
MISTRAL_API_KEY = ""  # 👈 METTEZ VOTRE CLÉ MISTRAL ICI

# Remplacez par :
MISTRAL_API_KEY = "votre_cle_mistral_ici"
```

### Comment ça Fonctionne

- ✅ **Mistral en priorité** : Si configuré, utilise Mistral
- ✅ **Hugging Face en fallback** : Si Mistral ne fonctionne pas, essaie Hugging Face
- ✅ **Message clair** : Si aucune API ne fonctionne, vous aurez un message explicite

## 💡 Avantages de Mistral

- ✅ **100% Gratuit** (avec quota généreux)
- ✅ **Excellent en français**
- ✅ **Rapide et fiable**
- ✅ **Facile à configurer**

## ❓ Besoin d'Aide ?

Consultez `GUIDE_MISTRAL.md` pour un guide détaillé.

## 🎉 C'est Tout !

Une fois votre clé configurée, l'IA fonctionnera automatiquement dans toute l'application !

