#!/bin/bash

echo "🚀 Démarrage de l'Assistant IA pour la Définition d'Objectifs..."
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
fi

echo "✅ Démarrage du serveur..."
echo "🌐 Ouvrez votre navigateur à l'adresse: http://localhost:5000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python3 app.py

