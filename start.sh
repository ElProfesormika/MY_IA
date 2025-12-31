#!/bin/bash

echo "Demarrage de l'Assistant IA pour la Definition d'Objectifs..."
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python3 n'est pas installe. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installation des dependances..."
    pip3 install -r requirements.txt
fi

echo "Demarrage du serveur..."
echo "Ouvrez votre navigateur a l'adresse: http://localhost:5000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python3 app.py




