#!/usr/bin/env python3
"""
Script de test pour la génération PDF
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_pdf

# Données de test
test_objectives = [
    {
        "goal": "Devenir très riche en 2026",
        "specific": "Créer un plan financier détaillé",
        "measurable": "Atteindre 500 000 € de patrimoine",
        "achievable": "J'ai les compétences nécessaires",
        "relevant": "C'est important pour ma famille",
        "time_bound": "Décembre 2026",
        "analysis": "Excellent objectif avec un plan clair"
    }
]

test_ikigai = {
    "what_you_love": "Créer des sites web",
    "what_you_are_good_at": "Raisonner et développer des théories",
    "what_world_needs": "Mettre la lumière sur des gens",
    "what_you_can_be_paid_for": "Création de sites web",
    "analysis": "Votre IKIGAI est clair : créer des sites web pour mettre en lumière des personnes."
}

print("Test de génération PDF...\n")

try:
    pdf_buffer = create_pdf(test_objectives, test_ikigai)
    
    if pdf_buffer:
        size = len(pdf_buffer.getvalue())
        print(f"PDF généré avec succès !")
        print(f"Taille du PDF: {size} bytes")
        
        if size > 0:
            print("Le PDF contient des données")
            
            # Sauvegarder pour test
            with open('test_output.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print("PDF sauvegardé dans test_output.pdf")
        else:
            print("Le PDF est vide")
    else:
        print("Le buffer PDF est None")
        
except Exception as e:
    print(f"ERREUR lors de la génération: {e}")
    import traceback
    traceback.print_exc()




