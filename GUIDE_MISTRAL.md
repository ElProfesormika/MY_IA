# 🚀 Guide pour Utiliser l'IA avec Mistral

## ✅ Solution Recommandée : API Mistral

L'API Mistral est **gratuite** (avec un quota généreux) et fonctionne **parfaitement en français** !

## 📝 Étapes pour Activer l'IA

### Étape 1 : Obtenir votre Clé API Mistral

1. **Allez sur** https://console.mistral.ai/
2. **Créez un compte** (c'est gratuit)
   - Cliquez sur "Sign Up" ou "S'inscrire"
   - Remplissez le formulaire
   - Confirmez votre email si nécessaire

3. **Obtenez votre clé API** :
   - Une fois connecté, allez dans **"API Keys"** (ou "Clés API")
   - Cliquez sur **"Create API Key"** (ou "Créer une clé API")
   - Donnez un nom à votre clé (ex: "mon-assistant-objectifs")
   - **Copiez la clé** immédiatement (elle commence souvent par des caractères aléatoires)

### Étape 2 : Configurer votre Application

1. **Ouvrez le fichier** `config.py`

2. **Trouvez cette ligne** :
   ```python
   MISTRAL_API_KEY = ""  # 👈 METTEZ VOTRE CLÉ MISTRAL ICI
   ```

3. **Collez votre clé API** :
   ```python
   MISTRAL_API_KEY = "votre_cle_mistral_ici"
   ```

4. **Sauvegardez le fichier**

### Étape 3 : Installer les Dépendances

```bash
pip install -r requirements.txt
```

Cela installera la bibliothèque `mistralai` nécessaire.

### Étape 4 : Tester

Lancez l'application :
```bash
python3 app.py
```

Puis ouvrez http://localhost:5000 dans votre navigateur.

## 🎯 Comment ça Fonctionne

L'application utilise maintenant **Mistral en priorité** :
- ✅ Si vous avez configuré Mistral → utilise Mistral
- ✅ Si Mistral ne fonctionne pas → essaie Hugging Face automatiquement
- ✅ Si aucune API ne fonctionne → message d'erreur clair

## 💡 Avantages de Mistral

- ✅ **Gratuit** jusqu'à un quota généreux
- ✅ **Excellent en français**
- ✅ **Rapide et fiable**
- ✅ **Facile à configurer**
- ✅ **Modèles de qualité**

## 🔧 Modèles Disponibles

Dans `config.py`, vous pouvez changer le modèle :

```python
MISTRAL_MODEL = "mistral-small-latest"  # Recommandé (bon équilibre)
# ou
MISTRAL_MODEL = "mistral-tiny-latest"   # Plus rapide, moins cher
# ou
MISTRAL_MODEL = "mistral-medium-latest" # Plus puissant (peut être payant)
```

## ❓ Problèmes Courants

### "ImportError: No module named 'mistralai'"
**Solution** : Installez les dépendances
```bash
pip install -r requirements.txt
```

### "Erreur d'authentification"
**Solution** : Vérifiez que votre clé API est correcte dans `config.py`

### "Quota dépassé"
**Solution** : Attendez quelques heures ou passez à un compte payant

## 🎉 C'est Prêt !

Une fois votre clé API Mistral configurée, l'IA fonctionnera automatiquement dans votre application !

