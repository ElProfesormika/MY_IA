let allObjectives = []; // Tous les objectifs SMART transformés
let ikigaiData = {};

// Gestion des étapes
function showStep(stepName) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step-${stepName}`).classList.add('active');
}

// Ajouter un objectif
function addObjective() {
    const list = document.getElementById('objectives-list');
    const count = list.children.length + 1;
    
    const newObjective = document.createElement('div');
    newObjective.className = 'objective-item';
    newObjective.innerHTML = `
        <div class="form-group">
            <label>Objectif #${count} *</label>
            <textarea class="objective-input" rows="3" placeholder="Ex: Je veux améliorer ma santé, apprendre une nouvelle langue, changer de carrière..."></textarea>
        </div>
    `;
    
    list.appendChild(newObjective);
}

// Créer un overlay de chargement
function showLoadingOverlay(message, submessage = '') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-overlay-content">
                <div class="loading-overlay-spinner"></div>
                <div class="loading-overlay-text">${message}</div>
                ${submessage ? `<div class="loading-overlay-subtext">${submessage}</div>` : ''}
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-overlay-text').textContent = message;
        const subtextEl = overlay.querySelector('.loading-overlay-subtext');
        if (subtextEl) {
            subtextEl.textContent = submessage;
        }
    }
    setTimeout(() => overlay.classList.add('active'), 10);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => {
            if (overlay && overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }, 300);
    }
}

// Traiter les objectifs avec l'IA
async function processObjectives() {
    const objectives = [];
    document.querySelectorAll('.objective-input').forEach(input => {
        const text = input.value.trim();
        if (text) {
            objectives.push(text);
        }
    });
    
    if (objectives.length === 0) {
        alert('Veuillez saisir au moins un objectif');
        return;
    }
    
    const btn = event.target;
    const spinner = btn.querySelector('.btn-spinner');
    const btnText = btn.querySelector('.btn-text');
    const originalText = btnText ? btnText.textContent : btn.textContent;
    
    // Afficher l'indicateur de chargement dans le bouton
    if (spinner) spinner.classList.remove('hidden');
    if (btnText) btnText.textContent = 'Traitement en cours...';
    btn.disabled = true;
    btn.classList.add('processing');
    
    // Afficher l'overlay de chargement
    showLoadingOverlay('Traitement de vos objectifs par l\'IA', `Analyse de ${objectives.length} objectif(s) en cours...`);
    
    try {
        const response = await fetch('/api/process-objectives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({ objectives: objectives }),
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors du traitement des objectifs');
        }
        
        const result = await response.json();
        allObjectives = result.objectives || [];
        
        // Afficher les résultats
        displaySMARTObjectives();
        
        // Passer à l'étape IKIGAI
        showStep('ikigai');
        
    } catch (error) {
        alert('Erreur lors du traitement des objectifs: ' + error.message);
    } finally {
        hideLoadingOverlay();
        const spinner = btn.querySelector('.btn-spinner');
        const btnText = btn.querySelector('.btn-text');
        if (spinner) spinner.classList.add('hidden');
        if (btnText) btnText.textContent = originalText;
        btn.disabled = false;
        btn.classList.remove('processing');
    }
}

// Afficher les objectifs SMART transformés - Chaque objectif traité individuellement
function displaySMARTObjectives() {
    const container = document.getElementById('smart-results');
    
    if (allObjectives.length === 0) {
        container.innerHTML = '<p>Aucun objectif traité.</p>';
        return;
    }
    
    let html = `<div class="objectives-summary">
        <p class="summary-text"><strong>${allObjectives.length}</strong> objectif(s) traité(s) individuellement par l'IA</p>
    </div>`;
    
    // Afficher chaque objectif avec un traitement spécifique et une séparation claire
    allObjectives.forEach((obj, idx) => {
        const objId = obj.objective_id || (idx + 1);
        const total = allObjectives.length;
        
        html += `
            <div class="smart-objective-card" data-objective-id="${objId}">
                <div class="objective-header">
                    <div class="objective-number-badge">Objectif #${objId}</div>
                    <h3 class="objective-title">${obj.goal || obj.original_text || 'Objectif'}</h3>
                    ${obj.original_text && obj.original_text !== obj.goal ? `
                    <p class="original-text"><em>Original : "${obj.original_text}"</em></p>
                    ` : ''}
                </div>
                
                <div class="smart-details">
                    <div class="smart-item">
                        <div class="smart-label">
                            <span class="smart-letter">S</span>
                            <strong>Spécifique:</strong>
                        </div>
                        <p>${obj.specific || (obj.goal || obj.original_text ? `Objectif spécifique : ${obj.goal || obj.original_text}. À préciser avec des détails concrets.` : 'À compléter')}</p>
                    </div>
                    
                    <div class="smart-item">
                        <div class="smart-label">
                            <span class="smart-letter">M</span>
                            <strong>Mesurable:</strong>
                        </div>
                        <p>${obj.measurable || (obj.goal || obj.original_text ? `Métriques à définir pour mesurer le succès de : ${obj.goal || obj.original_text}. Déterminer des indicateurs quantifiables.` : 'À compléter')}</p>
                    </div>
                    
                    <div class="smart-item">
                        <div class="smart-label">
                            <span class="smart-letter">A</span>
                            <strong>Atteignable:</strong>
                        </div>
                        <p>${obj.achievable || (obj.goal || obj.original_text ? `Évaluer la faisabilité de : ${obj.goal || obj.original_text}. Identifier les ressources nécessaires.` : 'À compléter')}</p>
                    </div>
                    
                    <div class="smart-item">
                        <div class="smart-label">
                            <span class="smart-letter">R</span>
                            <strong>Pertinent:</strong>
                        </div>
                        <p>${obj.relevant || (obj.goal || obj.original_text ? `Justifier l'importance de : ${obj.goal || obj.original_text}. Aligner avec les valeurs personnelles.` : 'À compléter')}</p>
                    </div>
                    
                    <div class="smart-item">
                        <div class="smart-label">
                            <span class="smart-letter">T</span>
                            <strong>Temporel:</strong>
                        </div>
                        <p>${obj.time_bound || (obj.goal || obj.original_text ? `Calendrier à définir pour : ${obj.goal || obj.original_text}. Fixer des dates précises et des jalons.` : 'À compléter')}</p>
                    </div>
                    
                    ${obj.analysis ? `
                    <div class="smart-analysis">
                        <strong>Analyse spécifique de cet objectif:</strong>
                        <p>${obj.analysis}</p>
                    </div>
                    ` : ''}
                </div>
                
                ${idx < total - 1 ? '<div class="objective-separator"></div>' : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Traiter l'IKIGAI
async function processIKIGAI() {
    const what_you_love = document.getElementById('what_you_love').value.trim();
    const what_you_are_good_at = document.getElementById('what_you_are_good_at').value.trim();
    const what_world_needs = document.getElementById('what_world_needs').value.trim();
    const what_you_can_be_paid_for = document.getElementById('what_you_can_be_paid_for').value.trim();
    
    if (!what_you_love || !what_you_are_good_at || !what_world_needs || !what_you_can_be_paid_for) {
        alert('Veuillez remplir tous les champs IKIGAI');
        return;
    }
    
    // Stocker les données IKIGAI
    ikigaiData = {
        what_you_love: what_you_love,
        what_you_are_good_at: what_you_are_good_at,
        what_world_needs: what_world_needs,
        what_you_can_be_paid_for: what_you_can_be_paid_for
    };
    
    const btn = event.target;
    const spinner = btn.querySelector('.btn-spinner');
    const btnText = btn.querySelector('.btn-text');
    const originalText = btnText ? btnText.textContent : btn.textContent;
    
    // Afficher l'indicateur de chargement dans le bouton
    if (spinner) spinner.classList.remove('hidden');
    if (btnText) btnText.textContent = 'Analyse en cours...';
    btn.disabled = true;
    btn.classList.add('processing');
    
    // Afficher l'overlay de chargement
    showLoadingOverlay('Analyse de votre IKIGAI', 'L\'IA révèle votre raison d\'être...');
    
    try {
        const response = await fetch('/api/analyze-ikigai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify(ikigaiData),
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de l\'analyse IKIGAI');
        }
        
        const result = await response.json();
        ikigaiData.analysis = result.analysis;
        
        // Afficher l'IKIGAI
        displayIKIGAI();
        
        // Passer à l'étape résultats
        showStep('results');
        
    } catch (error) {
        alert('Erreur lors de l\'analyse IKIGAI: ' + error.message);
    } finally {
        hideLoadingOverlay();
        const spinner = btn.querySelector('.btn-spinner');
        const btnText = btn.querySelector('.btn-text');
        if (spinner) spinner.classList.add('hidden');
        if (btnText) btnText.textContent = originalText;
        btn.disabled = false;
        btn.classList.remove('processing');
    }
}

// Afficher l'IKIGAI
function displayIKIGAI() {
    const container = document.getElementById('ikigai-content');
    const resultDiv = document.getElementById('ikigai-result');
    
    let html = `
        <div class="ikigai-details">
            <div class="ikigai-item">
                <strong>Ce que j'aime:</strong>
                <p>${(ikigaiData.what_you_love || '').trim()}</p>
            </div>
            <div class="ikigai-item">
                <strong>Ce en quoi je suis doué:</strong>
                <p>${(ikigaiData.what_you_are_good_at || '').trim()}</p>
            </div>
            <div class="ikigai-item">
                <strong>Ce dont le monde a besoin:</strong>
                <p>${(ikigaiData.what_world_needs || '').trim()}</p>
            </div>
            <div class="ikigai-item">
                <strong>Ce pour quoi je peux être payé:</strong>
                <p>${(ikigaiData.what_you_can_be_paid_for || '').trim()}</p>
            </div>
        </div>
    `;
    
    if (ikigaiData.analysis) {
        // Formater l'analyse avec les sections
        let formattedAnalysis = ikigaiData.analysis
            .replace(/##\s*(.+?)\n/g, '<h4>$1</h4>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        html += `
            <div class="ikigai-analysis">
                ${formattedAnalysis}
            </div>
        `;
    }
    
    container.innerHTML = html;
    resultDiv.style.display = 'block';
}

// Générer le PDF
async function generatePDF() {
    if (allObjectives.length === 0 && (!ikigaiData || !ikigaiData.what_you_love)) {
        alert('Veuillez d\'abord définir au moins un objectif ou compléter l\'IKIGAI');
        return;
    }
    
    const pdfBtn = document.getElementById('generate-pdf-btn');
    
    if (!pdfBtn) {
        console.error('Bouton PDF non trouvé');
        alert('Erreur: bouton non trouvé');
        return;
    }
    
    const spinner = pdfBtn.querySelector('.btn-spinner');
    const btnText = pdfBtn.querySelector('.btn-text');
    const originalText = btnText ? btnText.textContent : pdfBtn.textContent;
    
    // Désactiver le bouton et afficher le loading
    if (spinner) spinner.classList.remove('hidden');
    if (btnText) btnText.textContent = 'Génération en cours...';
    pdfBtn.disabled = true;
    pdfBtn.classList.add('processing');
    
    // Afficher l'overlay de chargement
    showLoadingOverlay('Génération de votre PDF', 'Création du document professionnel...');
    
    try {
        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({
                objectives: allObjectives,
                ikigai: ikigaiData
            }),
            cache: 'no-store'
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
            throw new Error(errorData.error || `Erreur ${response.status}`);
        }
        
        // Vérifier que c'est bien un PDF
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('pdf')) {
            throw new Error('La réponse n\'est pas un PDF valide');
        }
        
        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error('Le PDF généré est vide');
        }
        
        // Créer le lien de téléchargement immédiatement
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mes_objectifs_annee.pdf';
        a.style.display = 'none';
        document.body.appendChild(a);
        
        // Déclencher le téléchargement immédiatement
        a.click();
        
        // Nettoyer immédiatement
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            if (document.body.contains(a)) {
                document.body.removeChild(a);
            }
        }, 100);
        
        // Message de succès (optionnel, peut être retiré si trop intrusif)
        console.log('PDF généré et téléchargé avec succès !');
        
        // Afficher un message de succès brièvement
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            const textEl = overlay.querySelector('.loading-overlay-text');
            const subtextEl = overlay.querySelector('.loading-overlay-subtext');
            if (textEl) textEl.textContent = 'PDF généré avec succès !';
            if (subtextEl) subtextEl.textContent = 'Téléchargement en cours...';
            setTimeout(hideLoadingOverlay, 1500);
        } else {
            hideLoadingOverlay();
        }
        
    } catch (error) {
        console.error('Erreur PDF:', error);
        alert('Erreur lors de la génération du PDF: ' + error.message);
        hideLoadingOverlay();
    } finally {
        // Réactiver le bouton
        const spinner = pdfBtn.querySelector('.btn-spinner');
        const btnText = pdfBtn.querySelector('.btn-text');
        if (spinner) spinner.classList.add('hidden');
        if (btnText) btnText.textContent = originalText;
        pdfBtn.disabled = false;
        pdfBtn.classList.remove('processing');
    }
}
