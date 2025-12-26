"""
Point d'entrée pour Vercel
Importe l'application Flask depuis le répertoire parent
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel s'attend à un objet 'handler' ou 'app'
handler = app

