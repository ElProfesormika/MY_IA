"""
Point d'entrée pour Vercel
Importe l'application Flask depuis le répertoire parent
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Changer le répertoire de travail vers le parent pour que les chemins relatifs fonctionnent
os.chdir(parent_dir)

# Importer l'application Flask
try:
    from app import app
except Exception as e:
    # En cas d'erreur, créer une app Flask minimale pour le debug
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        import traceback
        error_msg = f"Erreur lors du chargement: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, 500

# Vercel détecte automatiquement l'objet Flask nommé 'app'
# Pas besoin de 'handler', Flask est détecté automatiquement
