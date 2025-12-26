# 🎯 Assistant IA pour la Définition d'Objectifs SMART & IKIGAI

Une application web intelligente qui vous aide à définir vos objectifs de l'année en utilisant les méthodes **SMART** et **IKIGAI**, avec l'aide de l'IA via l'API Hugging Face.

## ✨ Fonctionnalités

- **Objectifs SMART** : Définissez des objectifs Spécifiques, Mesurables, Atteignables, Pertinents et Temporels
- **IKIGAI** : Découvrez votre raison d'être en analysant vos passions, compétences, besoins du monde et valeur monétisable
- **Analyse IA** : Obtenez des recommandations personnalisées grâce à l'IA Hugging Face
- **Génération PDF** : Exportez vos objectifs et analyses dans un document PDF professionnel

## 🚀 Installation

1. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

2. **Lancer l'application** :
```bash
python app.py
```

3. **Ouvrir dans le navigateur** :
```
http://localhost:5000
```

## 📋 Utilisation

1. **Définir un objectif SMART** :
   - Remplissez tous les champs de la section SMART
   - Cliquez sur "Analyser avec l'IA" pour obtenir des recommandations
   
2. **Découvrir votre IKIGAI** :
   - Répondez aux 4 questions sur ce que vous aimez, vos compétences, les besoins du monde et votre valeur monétisable
   - Cliquez sur "Analyser avec l'IA" pour obtenir votre analyse IKIGAI personnalisée

3. **Générer le PDF** :
   - Après avoir rempli au moins une section et obtenu une analyse
   - Cliquez sur "Générer le PDF" pour télécharger votre document

## 🛠️ Technologies Utilisées

- **Backend** : Flask (Python)
- **IA** : Hugging Face API (Mistral-7B-Instruct)
- **PDF** : ReportLab
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)

## 📝 Structure du Projet

```
MY_AI/
├── app.py                 # Application Flask principale
├── config.py             # Configuration (clé API)
├── requirements.txt       # Dépendances Python
├── templates/
│   └── index.html        # Interface utilisateur
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── script.js     # Logique JavaScript
└── README.md             # Documentation
```

## 🎨 Interface

L'application dispose d'une interface moderne et intuitive avec :
- Design responsive (mobile-friendly)
- Animations fluides
- Couleurs dégradées modernes
- Expérience utilisateur optimisée

## 📄 Format PDF

Le PDF généré contient :
- Vos objectifs SMART détaillés avec analyse IA
- Votre analyse IKIGAI complète
- Mise en page professionnelle
- Date de génération

## ⚙️ Configuration

La clé API Hugging Face est configurée dans `config.py`. Pour utiliser une autre clé, modifiez le fichier `config.py`.

## 📌 Notes

- L'API Hugging Face peut prendre quelques secondes pour répondre
- Assurez-vous d'avoir une connexion internet active
- Le PDF est généré dynamiquement avec toutes vos données

## 🎉 Bonne définition d'objectifs !

