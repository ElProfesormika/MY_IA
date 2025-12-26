"""
Point d'entrée pour Vercel
Importe l'application Flask depuis le répertoire parent
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from app import app
    # Vercel s'attend à un objet 'handler' ou 'app'
    handler = app
except Exception as e:
    # En cas d'erreur, créer une app Flask minimale pour le debug
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/')
    def error_handler():
        return f"Erreur lors du chargement de l'application: {str(e)}", 500
    
    handler = error_app

