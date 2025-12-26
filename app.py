from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
import json
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importer config avec gestion d'erreur
try:
    import config
except ImportError:
    # Si config n'est pas trouvé, créer des valeurs par défaut
    import os
    class Config:
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
        MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
        HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL", "https://router.huggingface.co/models/google/flan-t5-base")
    config = Config()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration pour Vercel
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Désactiver le cache pour toutes les réponses
@app.after_request
def add_no_cache_headers(response):
    """Ajoute des headers pour désactiver le cache à chaque requête"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Configuration des APIs avec valeurs par défaut
try:
    MISTRAL_API_KEY = config.MISTRAL_API_KEY
    MISTRAL_MODEL = config.MISTRAL_MODEL
    HUGGINGFACE_API_KEY = config.HUGGINGFACE_API_KEY
    HUGGINGFACE_API_URL = config.HUGGINGFACE_API_URL
except AttributeError:
    # Si config n'a pas les attributs, utiliser os.getenv directement
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL", "https://router.huggingface.co/models/google/flan-t5-base")

def call_mistral_api(prompt):
    """Appelle l'API Mistral pour obtenir une réponse de l'IA"""
    if not MISTRAL_API_KEY or MISTRAL_API_KEY.strip() == "":
        return None  # Pas de clé API Mistral configurée
    
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        
        payload = {
            "model": MISTRAL_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1200  # Optimisé pour équilibrer qualité et vitesse
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('choices') and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                if content:
                    return content.strip()
        
        return None
        
    except Exception as e:
        return None  # Erreur, on essaiera Hugging Face

def call_huggingface_api(prompt):
    """Appelle l'API Hugging Face pour obtenir une réponse de l'IA"""
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    # Essayer plusieurs URLs si la première ne fonctionne pas
    urls_to_try = [
        HUGGINGFACE_API_URL,
        HUGGINGFACE_API_URL.replace("router.huggingface.co", "api-inference.huggingface.co"),
    ]
    
    for url in urls_to_try:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)  # Timeout optimisé pour rapidité
            
            if response.status_code == 200:
                result = response.json()
                
                # Gérer différents formats de réponse
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text:
                        return generated_text.strip()
                
                if isinstance(result, dict):
                    generated_text = result.get('generated_text', '') or result.get('text', '')
                    if generated_text:
                        return generated_text.strip()
                
                # Si la réponse est une string directement
                if isinstance(result, str):
                    return result.strip()
                
                # Fallback: analyser le texte brut
                text = str(result)
                if text and text != '{}' and text != '[]':
                    return text.strip()
                
                return "L'IA n'a pas pu générer de réponse. Veuillez réessayer."
                
            elif response.status_code == 503:
                return "Le modèle est en cours de chargement. Veuillez patienter quelques secondes et réessayer."
            elif response.status_code == 410:
                # Si erreur 410, essayer l'autre URL
                continue
            else:
                error_msg = f"Erreur API (code {response.status_code})"
                try:
                    error_detail = response.json()
                    if isinstance(error_detail, dict):
                        if 'error' in error_detail:
                            error_msg += f": {error_detail['error']}"
                        elif 'message' in error_detail:
                            error_msg += f": {error_detail['message']}"
                    elif isinstance(error_detail, str):
                        error_msg += f": {error_detail}"
                except:
                    error_text = response.text[:200] if response.text else ""
                    if error_text:
                        error_msg += f": {error_text}"
                # Si ce n'est pas la dernière URL, continuer
                if url != urls_to_try[-1]:
                    continue
                return error_msg
                
        except requests.exceptions.Timeout:
            if url == urls_to_try[-1]:  # Dernière URL
                return "Délai d'attente dépassé. L'API Hugging Face prend trop de temps à répondre. Veuillez réessayer."
            continue
        except requests.exceptions.RequestException as e:
            if url == urls_to_try[-1]:  # Dernière URL
                return f"Erreur de connexion à l'API: {str(e)}"
            continue
        except Exception as e:
            if url == urls_to_try[-1]:  # Dernière URL
                return f"Erreur lors de l'appel à l'API: {str(e)}"
            continue
    
    # Si toutes les URLs ont échoué
    return """❌ Impossible de se connecter à l'API Hugging Face.

💡 Solutions possibles:
1. Vérifiez votre clé API sur https://huggingface.co/settings/tokens
2. Le modèle peut ne pas être disponible via l'API gratuite
3. Essayez un autre modèle dans config.py (ex: google/flan-t5-large)
4. Consultez GUIDE_API.md pour plus d'aide"""

def call_ai_api(prompt):
    """Appelle l'API IA (Mistral en priorité, puis Hugging Face en fallback)"""
    # Essayer Mistral d'abord
    if MISTRAL_API_KEY:
        result = call_mistral_api(prompt)
        if result:
            return result
    
    # Fallback sur Hugging Face
    return call_huggingface_api(prompt)

def transform_objective_to_smart(objective_text, objective_number=None, total_objectives=None):
    """Transforme un objectif simple en format SMART avec l'IA - Traitement individuel et spécifique"""
    
    # Contexte pour personnaliser le traitement
    context_info = ""
    if objective_number and total_objectives:
        context_info = f"Cet objectif est le numéro {objective_number} sur {total_objectives} objectifs définis par cette personne. "
        if objective_number == 1:
            context_info += "C'est le premier objectif, donc probablement le plus prioritaire. "
        elif objective_number == total_objectives:
            context_info += "C'est le dernier objectif défini. "
    
    prompt = f"""Tu es un coach expert en développement personnel et en définition d'objectifs. {context_info}Une personne a écrit cet objectif spécifique :

"{objective_text}"

RÈGLES ABSOLUES :
1. Traite CET objectif de manière UNIQUE et SPÉCIFIQUE. Chaque objectif est différent.
2. Analyse-le en profondeur selon son domaine (professionnel, personnel, santé, finances, éducation, etc.).
3. Génère TOUJOURS des réponses COMPLÈTES et DÉTAILLÉES. JAMAIS de "À définir", "Non défini", ou valeurs vides.
4. Sois créatif, précis et actionnable. Chaque champ doit contenir au moins 2-3 phrases détaillées.

Transforme cet objectif en format SMART (Spécifique, Mesurable, Atteignable, Pertinent, Temporel) de manière professionnelle, motivante et TRÈS SPÉCIFIQUE à cet objectif précis.

CRITIQUE : Réponds UNIQUEMENT avec un JSON valide. Pas de texte avant, pas de texte après, pas de markdown, pas de backticks, pas de ```. Commence directement par {{ et termine par }}. Format exact :

{{
    "goal": "Objectif principal reformulé de manière claire, inspirante et précise - adapté spécifiquement à CET objectif. Minimum 10 mots.",
    "specific": "Description détaillée et précise : qui, quoi, où, comment, pourquoi. Sois très concret et spécifique à CET objectif. Détaille les actions précises. Minimum 20 mots avec exemples concrets.",
    "measurable": "Indicateurs de succès concrets avec chiffres, pourcentages, quantités. Comment saura-t-on que CET objectif est réussi ? Métriques précises avec valeurs numériques. Minimum 20 mots.",
    "achievable": "Pourquoi CET objectif est réaliste et atteignable ? Quelles ressources, compétences, soutiens sont disponibles pour CET objectif spécifique ? Détaille les moyens concrets. Minimum 20 mots.",
    "relevant": "Pourquoi CET objectif est important et aligné avec les valeurs et aspirations ? Quel impact spécifique aura-t-il sur la vie de cette personne ? Minimum 20 mots.",
    "time_bound": "Date limite précise et échéances intermédiaires pour CET objectif en 2026. Quand exactement sera-t-il atteint en 2026 ? Jalons clairs avec dates spécifiques (jour/mois/2026). Minimum 20 mots. IMPORTANT : Toutes les dates doivent être en 2026.",
    "analysis": "Analyse motivante en 5-7 phrases SPÉCIFIQUE à cet objectif : points forts de CET objectif, conseils pratiques personnalisés pour le réussir, étapes clés à suivre, risques à éviter, ressources à mobiliser. Minimum 50 mots."
}}

EXEMPLES DE BONNES RÉPONSES :
- "specific": "Je vais améliorer ma santé en faisant 30 minutes de sport 3 fois par semaine (lundi, mercredi, vendredi) le matin avant le travail, en suivant un programme d'entraînement personnalisé avec un coach."
- "measurable": "Je mesurerai mon succès par : perte de 5 kg en 3 mois, capacité à courir 5 km sans s'arrêter, réduction de 10 points de tension artérielle, et amélioration de mon niveau d'énergie de 30%."
- "time_bound": "Objectif final : 31 décembre 2026. Jalons 2026 : - 1er mars 2026 : perte de 2 kg - 1er juin 2026 : perte de 4 kg - 1er septembre 2026 : perte de 5 kg - 31 décembre 2026 : maintien du poids et forme optimale."

IMPORTANT : Nous sommes en 2026. Toutes les dates doivent être en 2026. L'année de référence est 2026.

Sois très concret, précis, motivant et actionnable. Utilise des exemples chiffrés et des dates précises EN 2026. Adapte ton analyse à la nature spécifique de CET objectif. RAPPEL : Nous sommes en 2026, toutes les dates doivent être en 2026. Réponds UNIQUEMENT le JSON, rien d'autre."""
    
    # Essayer jusqu'à 2 fois pour obtenir une réponse complète
    max_attempts = 2
    result = None
    
    for attempt in range(max_attempts):
        result = call_ai_api(prompt)
        if result and result.strip():
            # Vérifier que la réponse contient du contenu substantiel
            if len(result.strip()) > 50:  # Au moins 50 caractères
                break
        # Si c'est la dernière tentative, on continue quand même
        if attempt < max_attempts - 1:
            print(f"Tentative {attempt + 1} : réponse trop courte ou vide, nouvelle tentative...")
    
    if not result or not result.strip():
        # Si vraiment aucune réponse, on génère un objectif SMART basique mais structuré
        return {
            "goal": objective_text,
            "specific": f"Objectif à préciser : {objective_text}. À définir avec plus de détails sur qui, quoi, où, comment.",
            "measurable": f"Indicateurs de succès à déterminer pour : {objective_text}. Définir des métriques concrètes.",
            "achievable": f"Évaluer la faisabilité de : {objective_text}. Identifier les ressources nécessaires.",
            "relevant": f"Justifier l'importance de : {objective_text}. Aligner avec les valeurs personnelles.",
            "time_bound": f"Définir un calendrier pour : {objective_text}. Fixer des dates précises et des jalons.",
            "analysis": f"L'IA n'a pas pu traiter cet objectif automatiquement. Veuillez compléter manuellement les détails SMART pour : {objective_text}"
        }
    
    # Nettoyer la réponse : enlever markdown, backticks, etc.
    cleaned_result = result.strip()
    
    # Enlever les backticks et "json" si présents
    cleaned_result = re.sub(r'```json\s*', '', cleaned_result, flags=re.IGNORECASE)
    cleaned_result = re.sub(r'```\s*', '', cleaned_result)
    cleaned_result = cleaned_result.strip()
    
    # Méthode 1: Chercher un JSON complet entre accolades (gère les JSON multilignes)
    # On cherche le premier { et on trouve le } correspondant
    start_idx = cleaned_result.find('{')
    if start_idx != -1:
        # Compter les accolades pour trouver la fin
        brace_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(cleaned_result)):
            if cleaned_result[i] == '{':
                brace_count += 1
            elif cleaned_result[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx > start_idx:
            json_str = cleaned_result[start_idx:end_idx]
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict) and 'goal' in parsed:
                    return parsed
            except (json.JSONDecodeError, ValueError) as e:
                pass
    
    # Méthode 2: Essayer de parser directement
    try:
        parsed = json.loads(cleaned_result)
        if isinstance(parsed, dict) and 'goal' in parsed:
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Méthode 3: Extraire les champs individuellement avec regex améliorée
    # Gère les chaînes avec échappement et multilignes
    def extract_json_field(text, field_name):
        # Pattern pour capturer la valeur d'un champ JSON (gère les échappements)
        pattern = rf'"{field_name}"\s*:\s*"((?:[^"\\]|\\.)*)"'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Décoder les échappements JSON
            value = match.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            return value
        return None
    
    goal = extract_json_field(cleaned_result, 'goal')
    if goal:
        # Extraire tous les champs
        specific = extract_json_field(cleaned_result, 'specific')
        measurable = extract_json_field(cleaned_result, 'measurable')
        achievable = extract_json_field(cleaned_result, 'achievable')
        relevant = extract_json_field(cleaned_result, 'relevant')
        time_bound = extract_json_field(cleaned_result, 'time_bound')
        analysis = extract_json_field(cleaned_result, 'analysis')
        
        # Vérifier que les champs ne sont pas vides ou trop courts
        # Si un champ est vide ou trop court, on génère un contenu basé sur l'objectif
        def ensure_field(field_value, field_name, objective_text):
            if not field_value or len(field_value.strip()) < 10:
                # Générer un contenu basique mais structuré
                if field_name == 'specific':
                    return f"Objectif spécifique : {objective_text}. À préciser avec plus de détails sur les actions concrètes à entreprendre."
                elif field_name == 'measurable':
                    return f"Métriques à définir pour mesurer le succès de : {objective_text}. Déterminer des indicateurs quantifiables."
                elif field_name == 'achievable':
                    return f"Évaluer la faisabilité de : {objective_text}. Identifier les ressources, compétences et soutiens nécessaires."
                elif field_name == 'relevant':
                    return f"Justifier l'importance de : {objective_text}. Aligner avec les valeurs, aspirations et objectifs de vie."
                elif field_name == 'time_bound':
                    return f"Calendrier à définir pour : {objective_text}. Fixer des dates précises et des jalons intermédiaires."
                elif field_name == 'analysis':
                    return f"Analyse de l'objectif : {objective_text}. Points à considérer : définir les étapes clés, identifier les ressources nécessaires, anticiper les défis potentiels."
            return field_value
        
        return {
            "goal": goal if goal and len(goal.strip()) >= 5 else objective_text,
            "specific": ensure_field(specific, 'specific', objective_text),
            "measurable": ensure_field(measurable, 'measurable', objective_text),
            "achievable": ensure_field(achievable, 'achievable', objective_text),
            "relevant": ensure_field(relevant, 'relevant', objective_text),
            "time_bound": ensure_field(time_bound, 'time_bound', objective_text),
            "analysis": ensure_field(analysis, 'analysis', objective_text)
        }
    
    # Dernier recours : si on trouve au moins "goal", on utilise ce qu'on peut
    if '"goal"' in cleaned_result or "'goal'" in cleaned_result:
        # L'IA a essayé de faire du JSON mais c'est mal formaté
        # On extrait ce qu'on peut et on génère le reste
        goal_extracted = extract_json_field(cleaned_result, 'goal') or objective_text
        specific_extracted = extract_json_field(cleaned_result, 'specific')
        measurable_extracted = extract_json_field(cleaned_result, 'measurable')
        achievable_extracted = extract_json_field(cleaned_result, 'achievable')
        relevant_extracted = extract_json_field(cleaned_result, 'relevant')
        time_bound_extracted = extract_json_field(cleaned_result, 'time_bound')
        analysis_extracted = extract_json_field(cleaned_result, 'analysis')
        
        # Générer des contenus structurés même si incomplets
        return {
            "goal": goal_extracted if goal_extracted and len(goal_extracted.strip()) >= 5 else objective_text,
            "specific": specific_extracted if specific_extracted and len(specific_extracted.strip()) >= 10 else f"Objectif spécifique : {objective_text}. À préciser avec des détails concrets sur les actions à entreprendre.",
            "measurable": measurable_extracted if measurable_extracted and len(measurable_extracted.strip()) >= 10 else f"Métriques à définir pour mesurer le succès de : {objective_text}. Déterminer des indicateurs quantifiables (chiffres, pourcentages, quantités).",
            "achievable": achievable_extracted if achievable_extracted and len(achievable_extracted.strip()) >= 10 else f"Évaluer la faisabilité de : {objective_text}. Identifier les ressources, compétences et soutiens nécessaires pour atteindre cet objectif.",
            "relevant": relevant_extracted if relevant_extracted and len(relevant_extracted.strip()) >= 10 else f"Justifier l'importance de : {objective_text}. Aligner avec les valeurs, aspirations et objectifs de vie personnels.",
            "time_bound": time_bound_extracted if time_bound_extracted and len(time_bound_extracted.strip()) >= 10 else f"Calendrier à définir pour : {objective_text}. Fixer des dates précises en 2026 (jour/mois/2026) et des jalons intermédiaires pour 2026.",
            "analysis": analysis_extracted if analysis_extracted and len(analysis_extracted.strip()) >= 20 else f"Analyse de l'objectif : {objective_text}. Points à considérer : définir les étapes clés, identifier les ressources nécessaires, anticiper les défis potentiels, et planifier les actions concrètes."
        }
    
    # Aucun JSON trouvé - Générer un objectif SMART structuré basé sur le texte original
    return {
        "goal": objective_text,
        "specific": f"Objectif spécifique : {objective_text}. À préciser avec des détails concrets sur qui, quoi, où, comment, pourquoi. Détailler les actions précises à entreprendre.",
        "measurable": f"Métriques à définir pour mesurer le succès de : {objective_text}. Déterminer des indicateurs quantifiables avec des chiffres, pourcentages ou quantités précises.",
        "achievable": f"Évaluer la faisabilité de : {objective_text}. Identifier les ressources, compétences, soutiens et moyens disponibles pour atteindre cet objectif de manière réaliste.",
        "relevant": f"Justifier l'importance de : {objective_text}. Aligner avec les valeurs personnelles, aspirations et objectifs de vie. Définir l'impact positif attendu.",
        "time_bound": f"Calendrier à définir pour : {objective_text}. Fixer des dates précises en 2026 (jour/mois/2026) pour l'objectif final et des jalons intermédiaires pour suivre la progression tout au long de 2026.",
        "analysis": f"Analyse de l'objectif : {objective_text}. Pour réussir cet objectif, il est important de : 1) Définir des étapes clés concrètes, 2) Identifier les ressources nécessaires, 3) Anticiper les défis potentiels, 4) Planifier les actions concrètes, 5) Suivre régulièrement la progression."
    }

def generate_ikigai_analysis(what_you_love, what_you_are_good_at, what_world_needs, what_you_can_be_paid_for):
    """Génère une analyse IKIGAI avec l'IA à partir de réponses simples - Version optimisée pour rapidité"""
    prompt = f"""Tu es un coach expert en IKIGAI (raison d'être) et développement personnel. Analyse ces réponses pour révéler l'IKIGAI de cette personne. Sois concis mais complet :

CE QUE J'AIME : {what_you_love}

CE EN QUOI JE SUIS DOUÉ : {what_you_are_good_at}

CE DONT LE MONDE A BESOIN : {what_world_needs}

CE POUR QUOI JE PEUX ÊTRE PAYÉ : {what_you_can_be_paid_for}

Structure ta réponse de manière claire et inspirante :

## 🌟 TON IKIGAI (Raison d'Être)

[Identifie l'intersection unique de ces 4 éléments. Formule un IKIGAI personnalisé et inspirant en 2-3 phrases]

## 💡 ANALYSE ET INSIGHTS

[Analyse les connexions entre ces 4 éléments. Qu'est-ce qui ressort ? Quelles sont les opportunités ?]

## 🎯 RECOMMANDATIONS CONCRÈTES

[3-5 recommandations actionnables pour vivre son IKIGAI au quotidien]

## 🚀 PISTES D'ACTION POUR 2026

[3-5 actions concrètes à entreprendre en 2026 pour aligner sa vie avec son IKIGAI]

Sois inspirant, concret, motivant et actionnable. Utilise un ton positif et encourageant. RAPPEL : Nous sommes en 2026, toutes les actions et dates doivent être pour l'année 2026."""
    
    # Appel direct à Mistral pour IKIGAI (plus rapide, pas besoin de fallback)
    result = call_mistral_api(prompt) if MISTRAL_API_KEY else call_ai_api(prompt)
    
    if not result or len(result.strip()) < 50:
        # Générer une analyse basique structurée
        return f"""## 🌟 TON IKIGAI (Raison d'Être)

L'intersection de ce que tu aimes ({what_you_love[:100] if what_you_love else 'tes passions'}...), ce en quoi tu es doué ({what_you_are_good_at[:100] if what_you_are_good_at else 'tes compétences'}...), ce dont le monde a besoin ({what_world_needs[:100] if what_world_needs else 'les besoins du monde'}...), et ce pour quoi tu peux être payé ({what_you_can_be_paid_for[:100] if what_you_can_be_paid_for else 'tes services'}...) révèle ton IKIGAI unique.

## 💡 ANALYSE ET INSIGHTS

Ces quatre éléments se complètent et révèlent des opportunités intéressantes. Il est important de trouver l'équilibre entre passion, compétence, impact et rémunération.

## 🎯 RECOMMANDATIONS CONCRÈTES

1. Explore les intersections entre tes passions et tes compétences
2. Identifie les besoins du marché qui correspondent à tes talents
3. Développe des compétences complémentaires pour renforcer ton IKIGAI
4. Crée des opportunités qui allient passion et rémunération

## 🚀 PISTES D'ACTION POUR 2026

1. Définir des objectifs SMART alignés avec ton IKIGAI pour 2026
2. Chercher des opportunités en 2026 qui combinent tes 4 éléments
3. Développer un plan d'action concret pour vivre ton IKIGAI en 2026
4. Suivre régulièrement ta progression vers ton IKIGAI tout au long de 2026"""
    
    return result.strip()

def clean_text_for_pdf(text):
    """Nettoie le texte pour éviter les erreurs dans le PDF - Version améliorée"""
    if not text:
        return ""
    import re
    # Convertir en string
    text = str(text)
    
    # Supprimer les null bytes et caractères de contrôle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Nettoyer les balises markdown (en plusieurs passes pour éviter les conflits)
    # D'abord les blocs de code
    text = re.sub(r'```[\w]*\n.*?```', '', text, flags=re.DOTALL)  # Supprimer les blocs de code complets
    text = re.sub(r'```', '', text)  # Supprimer les ``` restants
    
    # Ensuite les gras et italiques (ordre important)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **texte** -> texte (gras markdown)
    text = re.sub(r'__(.+?)__', r'\1', text)  # __texte__ -> texte (gras markdown alternatif)
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # *texte* -> texte (italique markdown, mais attention aux astérisques seuls)
    text = re.sub(r'_(.+?)_', r'\1', text)  # _texte_ -> texte (italique markdown)
    
    # Nettoyer les titres markdown
    text = re.sub(r'##+\s*(.+?)(?:\n|$)', r'\1\n', text)  # ## Titre -> Titre
    text = re.sub(r'#+\s*(.+?)(?:\n|$)', r'\1\n', text)  # # Titre -> Titre
    
    # Nettoyer le code inline
    text = re.sub(r'`(.+?)`', r'\1', text)  # `code` -> code
    
    # Nettoyer les listes markdown
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Supprimer les puces de liste
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Supprimer les numéros de liste
    
    # Échapper les caractères HTML/XML pour ReportLab
    text = re.sub(r'&(?![a-zA-Z]+;)', '&amp;', text)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Réinsérer uniquement les balises HTML nécessaires pour ReportLab
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    text = text.replace('&lt;br/&gt;', '<br/>').replace('&lt;br&gt;', '<br/>')
    text = text.replace('&lt;p&gt;', '<p>').replace('&lt;/p&gt;', '</p>')
    
    # Nettoyer les espaces multiples
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 retours à la ligne consécutifs
    
    return text.strip()

def create_pdf(objectives_list, ikigai_data, filename='objectifs_annee.pdf'):
    """Crée un PDF avec les objectifs SMART et IKIGAI - Version optimisée et robuste"""
    buffer = io.BytesIO()
    
    # Marges équilibrées pour une meilleure présentation
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           leftMargin=0.7*inch, rightMargin=0.7*inch,
                           topMargin=0.6*inch, bottomMargin=0.6*inch)
    story = []
    
    # Styles améliorés pour une meilleure présentation
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#3498db'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # En-tête avec logo et branding - taille améliorée
    try:
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo_BuildNovaG.jpg')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=0.8*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.1*inch))
    except:
        pass
    
    # BuildNovaG en or - style amélioré
    story.append(Paragraph("<b>BuildNovaG</b>", ParagraphStyle(
        'BrandStyleGold',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=colors.HexColor('#DAA520'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Objectifs-AI", ParagraphStyle(
        'TaglineStyle',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.white,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontStyle='italic',
        fontWeight='bold',
        backColor=colors.HexColor('#667eea'),
        borderPadding=5
    )))
    story.append(Spacer(1, 0.15*inch))
    # "Heureuse Année 2026" avec fond dégradé blanc
    new_year_table_data = [[Paragraph("<b>Heureuse Année 2026</b>", ParagraphStyle(
        'NewYearStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#e74c3c'),
        alignment=TA_CENTER,
        fontStyle='italic',
        fontName='Helvetica-Bold',
        fontWeight='bold'
    ))]]
    new_year_table = Table(new_year_table_data, colWidths=[6*inch], rowHeights=[0.5*inch])
    new_year_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8f9fa')]),
    ]))
    story.append(new_year_table)
    story.append(Spacer(1, 0.2*inch))
    story.append(Spacer(1, 0.2*inch))
    
    # Titre principal
    story.append(Paragraph("Mes Objectifs pour l'Année 2026", title_style))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(f"<i>Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>", 
                          ParagraphStyle('DateStyle', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.HexColor('#666'), fontSize=10)))
    story.append(Spacer(1, 0.4*inch))
    
    # Section SMART - Traitement INDIVIDUEL et SPÉCIFIQUE pour chaque objectif
    if objectives_list and len(objectives_list) > 0:
        # En-tête de section avec nombre d'objectifs
        total_obj = len(objectives_list)
        section_title = f"🎯 Mes Objectifs SMART ({total_obj} objectif{'s' if total_obj > 1 else ''} traité{'s' if total_obj > 1 else ''} individuellement)"
        story.append(Paragraph(section_title, heading_style))
        story.append(Spacer(1, 0.3*inch))
        
        for idx, smart_data in enumerate(objectives_list, 1):
            # Obtenir l'ID de l'objectif (utiliser objective_id si disponible)
            obj_id = smart_data.get('objective_id', idx)
            total_objs = len(objectives_list)
            
            # Séparation visuelle marquée entre les objectifs (sauf pour le premier)
            if idx > 1:
                story.append(Spacer(1, 0.4*inch))
                # Ligne de séparation plus visible
                separator_table = Table([['']], colWidths=[6*inch], rowHeights=[0.03*inch])
                separator_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
                    ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#667eea')),
                ]))
                story.append(separator_table)
                story.append(Spacer(1, 0.4*inch))
            
            # Encadré pour chaque objectif avec fond coloré - TRAITEMENT INDIVIDUEL
            goal_clean = clean_text_for_pdf(smart_data.get('goal', 'Objectif'))
            original_text = smart_data.get('original_text', '')
            
            # En-tête de l'objectif avec fond coloré et numéro
            obj_header_text = f"<b>OBJECTIF #{obj_id} / {total_objs}</b>"
            if idx == 1:
                obj_header_text += " <i>(Prioritaire)</i>"
            
            obj_header_data = [[Paragraph(obj_header_text, 
                                         ParagraphStyle('ObjNum', parent=styles['Normal'], 
                                                       fontSize=13, fontName='Helvetica-Bold',
                                                       textColor=colors.white,
                                                       alignment=TA_CENTER))]]
            obj_header = Table(obj_header_data, colWidths=[6*inch], rowHeights=[0.45*inch])
            obj_header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(obj_header)
            story.append(Spacer(1, 0.2*inch))
            
            # Titre de l'objectif (reformulé par l'IA)
            story.append(Paragraph(f"<b>{goal_clean}</b>", 
                                  ParagraphStyle('ObjTitle', parent=styles['Heading3'], fontSize=18, 
                                                textColor=colors.HexColor('#2c3e50'), spaceAfter=12, spaceBefore=8,
                                                fontName='Helvetica-Bold', alignment=TA_CENTER)))
            
            # Afficher le texte original si différent du goal reformulé
            if original_text and original_text.strip() and original_text.strip() != goal_clean:
                original_clean = clean_text_for_pdf(original_text)
                story.append(Paragraph(f"<i>Objectif original : \"{original_clean}\"</i>", 
                                      ParagraphStyle('OriginalText', parent=styles['Italic'], fontSize=9, 
                                                    textColor=colors.HexColor('#666'), spaceAfter=15, 
                                                    alignment=TA_CENTER)))
            
            story.append(Spacer(1, 0.25*inch))
            
            # Tableau SMART amélioré - utiliser Paragraph pour gérer les retours à la ligne
            def prepare_table_cell(text):
                """Prépare une cellule de tableau avec Paragraph pour gérer les retours à la ligne"""
                text = clean_text_for_pdf(text)
                if not text or text.strip() == '':
                    # Au lieu de "Non défini", générer un texte structuré basé sur l'objectif
                    goal_for_context = clean_text_for_pdf(smart_data.get('goal', smart_data.get('original_text', 'Objectif')))
                    return Paragraph(f'À compléter pour : {goal_for_context[:50]}...', 
                                    ParagraphStyle('CellText', parent=styles['Normal'], fontSize=9, 
                                                  textColor=colors.HexColor('#999'), fontStyle='italic'))
                # Remplacer les retours à la ligne par <br/>
                text = text.replace('\n', '<br/>')
                return Paragraph(text, ParagraphStyle('CellText', parent=styles['Normal'], fontSize=10, leading=12))
            
            smart_table_data = [
                [Paragraph('<b>Critère</b>', ParagraphStyle('HeaderText', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')), 
                 Paragraph('<b>Détails</b>', ParagraphStyle('HeaderText', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold'))],
                [Paragraph('<b>S - Spécifique</b>', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
                 prepare_table_cell(smart_data.get('specific', 'Non défini'))],
                [Paragraph('<b>M - Mesurable</b>', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
                 prepare_table_cell(smart_data.get('measurable', 'Non défini'))],
                [Paragraph('<b>A - Atteignable</b>', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
                 prepare_table_cell(smart_data.get('achievable', 'Non défini'))],
                [Paragraph('<b>R - Pertinent</b>', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
                 prepare_table_cell(smart_data.get('relevant', 'Non défini'))],
                [Paragraph('<b>T - Temporel</b>', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
                 prepare_table_cell(smart_data.get('time_bound', 'Non défini'))],
            ]
            
            smart_table = Table(smart_table_data, colWidths=[1.8*inch, 4.2*inch], repeatRows=1)
            # Style amélioré pour meilleure lisibilité
            smart_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e8f4f8')),  # Colonne gauche avec fond léger
                ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Colonne droite blanche
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),  # Alternance de couleurs
            ]))
            story.append(smart_table)
            
            # Analyse améliorée - texte complet SPÉCIFIQUE à cet objectif dans une boîte
            if smart_data.get('analysis'):
                story.append(Spacer(1, 0.25*inch))
                analysis_text = clean_text_for_pdf(smart_data.get('analysis', ''))
                # Remplacer les retours à la ligne par <br/>
                analysis_text = analysis_text.replace('\n', '<br/>')
                
                # Boîte pour l'analyse avec fond coloré - Analyse SPÉCIFIQUE de cet objectif
                analysis_title = f"<b>💡 Analyse Spécifique de l'Objectif #{obj_id}:</b>"
                full_analysis = f"{analysis_title}<br/><br/>{analysis_text}"
                analysis_box_data = [[Paragraph(full_analysis, ParagraphStyle(
                    'AnalysisText', parent=styles['Normal'], fontSize=10, 
                    textColor=colors.HexColor('#495057'),
                    leading=13))]]
                analysis_box = Table(analysis_box_data, colWidths=[6*inch])
                analysis_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#ffd700')),
                ]))
                story.append(analysis_box)
            
            # Espacement final après chaque objectif - TRAITEMENT INDIVIDUEL
            story.append(Spacer(1, 0.4*inch))
            
            # Note de traitement individuel pour chaque objectif (sauf le dernier)
            if idx < len(objectives_list):
                note_text = f"<i>Objectif #{obj_id} traité individuellement par l'IA</i>"
                story.append(Paragraph(note_text, ParagraphStyle(
                    'ObjNote', parent=styles['Italic'], fontSize=8, 
                    textColor=colors.HexColor('#999'), alignment=TA_CENTER, spaceAfter=15)))
            
            # Saut de page après chaque objectif (sauf le dernier) si on a plusieurs objectifs
            # Cela permet à chaque objectif d'avoir sa propre page pour un meilleur traitement individuel
            if idx < len(objectives_list) and len(objectives_list) > 1:
                story.append(PageBreak())
        
        # Saut de page seulement si on a aussi une section IKIGAI
        if ikigai_data and (ikigai_data.get('what_you_love') or ikigai_data.get('what_you_are_good_at')):
            story.append(PageBreak())
    
    # Section IKIGAI - Style amélioré
    if ikigai_data and (ikigai_data.get('what_you_love') or ikigai_data.get('what_you_are_good_at')):
        story.append(Paragraph("🌸 Mon IKIGAI", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Tableau IKIGAI amélioré - utiliser Paragraph pour gérer les retours à la ligne
        def prepare_table_cell(text):
            """Prépare une cellule de tableau avec Paragraph pour gérer les retours à la ligne"""
            text = clean_text_for_pdf(text)
            if not text or text.strip() == '':
                return Paragraph('Non défini', ParagraphStyle('CellText', parent=styles['Normal'], fontSize=10))
            # Remplacer les retours à la ligne par <br/>
            text = text.replace('\n', '<br/>')
            return Paragraph(text, ParagraphStyle('CellText', parent=styles['Normal'], fontSize=10, leading=12))
        
        ikigai_table_data = [
            [Paragraph('<b>Élément</b>', ParagraphStyle('HeaderText', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')), 
             Paragraph('<b>Détails</b>', ParagraphStyle('HeaderText', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold'))],
            [Paragraph('Ce que j\'aime', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
             prepare_table_cell(ikigai_data.get('what_you_love', 'Non défini'))],
            [Paragraph('Ce en quoi je suis doué', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
             prepare_table_cell(ikigai_data.get('what_you_are_good_at', 'Non défini'))],
            [Paragraph('Ce dont le monde a besoin', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
             prepare_table_cell(ikigai_data.get('what_world_needs', 'Non défini'))],
            [Paragraph('Ce pour quoi je peux être payé', ParagraphStyle('LabelText', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold')), 
             prepare_table_cell(ikigai_data.get('what_you_can_be_paid_for', 'Non défini'))],
        ]
        
        ikigai_table = Table(ikigai_table_data, colWidths=[2*inch, 4*inch], repeatRows=1)
        ikigai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ffe8e8')),  # Colonne gauche avec fond rose léger
            ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Colonne droite blanche
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),  # Alternance de couleurs
        ]))
        story.append(ikigai_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Analyse IKIGAI améliorée - texte complet sans limitation
        if ikigai_data.get('analysis'):
            analysis_text = clean_text_for_pdf(ikigai_data.get('analysis', ''))
            # Remplacer les retours à la ligne par <br/>
            analysis_text = analysis_text.replace('\n', '<br/>')
            
            story.append(Paragraph("<b>💡 Analyse IKIGAI:</b>", ParagraphStyle(
                'IKIGAITitle', parent=styles['Heading4'], fontSize=11, 
                textColor=colors.HexColor('#2c3e50'), spaceAfter=5, fontName='Helvetica-Bold')))
            
            story.append(Paragraph(analysis_text, ParagraphStyle(
                'IKIGAIText',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#495057'),
                leftIndent=10,
                spaceAfter=8,
                leading=13
            )))
    
    # Footer amélioré
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("<i>Document généré par BuildNovaG Objectifs-AI</i>", 
                          ParagraphStyle('FooterStyle', parent=styles['Italic'], alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor('#999'))))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("<b>www.buildnovag.fr</b>", 
                          ParagraphStyle('FooterLink', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#667eea'), fontName='Helvetica-Bold')))
    
    # Génération optimisée avec gestion d'erreurs robuste
    try:
        doc.build(story)
    except Exception as e:
        # En cas d'erreur, logger et réessayer
        print(f"Erreur génération PDF: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Impossible de générer le PDF: {str(e)}")
    
    buffer.seek(0)
    
    # Vérifier que le buffer contient des données
    if buffer.getvalue() == b'':
        raise Exception("Le PDF généré est vide")
    
    return buffer

@app.route('/')
def index():
    """Page d'accueil - avec headers no-cache"""
    response = app.make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/process-objectives', methods=['POST'])
def process_objectives():
    """Transforme les objectifs bruts en format SMART - Traitement individuel et spécifique pour chaque objectif"""
    data = request.json
    objectives = data.get('objectives', [])
    
    if not objectives:
        return jsonify({'error': 'Aucun objectif fourni'}), 400
    
    # Filtrer les objectifs vides
    valid_objectives = [obj.strip() for obj in objectives if obj.strip()]
    
    if not valid_objectives:
        return jsonify({'error': 'Aucun objectif valide fourni'}), 400
    
    total_objectives = len(valid_objectives)
    smart_objectives = []
    
    # Fonction pour traiter un objectif individuellement
    def process_single_objective(idx_obj_tuple):
        idx, obj_text = idx_obj_tuple
        try:
            # Traitement spécifique pour chaque objectif avec son contexte
            smart_obj = transform_objective_to_smart(
                obj_text, 
                objective_number=idx, 
                total_objectives=total_objectives
            )
            
            # Ajouter un identifiant unique pour chaque objectif
            smart_obj['objective_id'] = idx
            smart_obj['original_text'] = obj_text
            
            return (idx, smart_obj)
            
        except Exception as e:
            # En cas d'erreur pour un objectif, créer un objectif SMART structuré même sans IA
            print(f"Erreur lors du traitement de l'objectif #{idx}: {e}")
            import traceback
            traceback.print_exc()
            
            # Générer un objectif SMART basique mais structuré
            return (idx, {
                "objective_id": idx,
                "original_text": obj_text,
                "goal": obj_text,
                "specific": f"Objectif spécifique : {obj_text}. À préciser avec des détails concrets sur qui, quoi, où, comment, pourquoi. Détailler les actions précises à entreprendre.",
                "measurable": f"Métriques à définir pour mesurer le succès de : {obj_text}. Déterminer des indicateurs quantifiables avec des chiffres, pourcentages ou quantités précises.",
                "achievable": f"Évaluer la faisabilité de : {obj_text}. Identifier les ressources, compétences, soutiens et moyens disponibles pour atteindre cet objectif de manière réaliste.",
                "relevant": f"Justifier l'importance de : {obj_text}. Aligner avec les valeurs personnelles, aspirations et objectifs de vie. Définir l'impact positif attendu.",
                "time_bound": f"Calendrier à définir pour : {obj_text}. Fixer des dates précises en 2026 (jour/mois/2026) pour l'objectif final et des jalons intermédiaires pour suivre la progression tout au long de 2026.",
                "analysis": f"Analyse de l'objectif : {obj_text}. Pour réussir cet objectif, il est important de : 1) Définir des étapes clés concrètes, 2) Identifier les ressources nécessaires, 3) Anticiper les défis potentiels, 4) Planifier les actions concrètes, 5) Suivre régulièrement la progression. Note : L'IA n'a pas pu traiter cet objectif automatiquement, veuillez compléter les détails manuellement."
            })
    
    # Traitement PARALLÈLE pour accélérer (max 3 threads pour éviter de surcharger l'API)
    max_workers = min(3, total_objectives)  # Maximum 3 objectifs en parallèle
    objectives_with_index = [(idx, obj_text) for idx, obj_text in enumerate(valid_objectives, 1)]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumettre toutes les tâches
        future_to_index = {executor.submit(process_single_objective, obj_data): obj_data[0] 
                          for obj_data in objectives_with_index}
        
        # Collecter les résultats au fur et à mesure
        results = {}
        for future in as_completed(future_to_index):
            try:
                idx, smart_obj = future.result()
                results[idx] = smart_obj
            except Exception as e:
                idx = future_to_index[future]
                print(f"Erreur critique pour l'objectif #{idx}: {e}")
                # Créer un objectif par défaut en cas d'erreur critique
                obj_text = valid_objectives[idx - 1]
                results[idx] = {
                    "objective_id": idx,
                    "original_text": obj_text,
                    "goal": obj_text,
                    "specific": f"Objectif spécifique : {obj_text}. À préciser avec des détails concrets.",
                    "measurable": f"Métriques à définir pour : {obj_text}.",
                    "achievable": f"Évaluer la faisabilité de : {obj_text}.",
                    "relevant": f"Justifier l'importance de : {obj_text}.",
                    "time_bound": f"Calendrier à définir pour : {obj_text}.",
                    "analysis": f"Analyse de l'objectif : {obj_text}. Erreur lors du traitement."
                }
    
    # Trier les résultats par index pour maintenir l'ordre
    smart_objectives = [results[idx] for idx in sorted(results.keys())]
    
    return jsonify({
        'objectives': smart_objectives,
        'total_processed': len(smart_objectives),
        'message': f'{len(smart_objectives)} objectif(s) traité(s) individuellement'
    })

@app.route('/api/analyze-ikigai', methods=['POST'])
def analyze_ikigai():
    """Génère l'analyse IKIGAI à partir des réponses simples"""
    data = request.json
    analysis = generate_ikigai_analysis(
        data.get('what_you_love', ''),
        data.get('what_you_are_good_at', ''),
        data.get('what_world_needs', ''),
        data.get('what_you_can_be_paid_for', '')
    )
    return jsonify({'analysis': analysis})

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Génère le PDF avec tous les objectifs SMART et l'IKIGAI - Version optimisée"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
            
        objectives = data.get('objectives', [])  # Liste d'objectifs SMART
        ikigai_data = data.get('ikigai', {})
        
        if not objectives and not ikigai_data:
            return jsonify({'error': 'Aucune donnée à générer. Veuillez d\'abord définir des objectifs ou compléter l\'IKIGAI.'}), 400
        
        # Générer le PDF
        pdf_buffer = create_pdf(objectives, ikigai_data)
        
        # Vérifier que le buffer contient des données
        if not pdf_buffer:
            return jsonify({'error': 'Le PDF généré est vide'}), 500
        
        # Obtenir la taille avant de seek pour éviter de relire
        pdf_data = pdf_buffer.getvalue()
        if pdf_data == b'':
            return jsonify({'error': 'Le PDF généré est vide'}), 500
        
        # Créer un nouveau buffer en mémoire pour la réponse
        response_buffer = io.BytesIO(pdf_data)
        response_buffer.seek(0)
        
        # Créer la réponse avec headers optimisés
        response = send_file(
            response_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='mes_objectifs_annee.pdf'
        )
        
        # Ajouter des headers pour forcer le téléchargement et optimiser
        response.headers['Content-Disposition'] = 'attachment; filename=mes_objectifs_annee.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Length'] = str(len(pdf_data))
        # Désactiver la mise en cache pour éviter les problèmes
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except ValueError as e:
        return jsonify({'error': f'Erreur de format de données: {str(e)}'}), 400
    except IOError as e:
        return jsonify({'error': f'Erreur d\'écriture du PDF: {str(e)}'}), 500
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la génération du PDF: {error_msg}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

