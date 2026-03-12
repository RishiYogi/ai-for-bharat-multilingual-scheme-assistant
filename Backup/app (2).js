// API Configuration
const API_ENDPOINT = 'https://wgwpbn481c.execute-api.ap-south-1.amazonaws.com/query';

// Language selection
let selectedLanguage = 'English';

// Language code mapping (ISO-639-1)
const languageCodes = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta'
};

function selectLanguage(language) {
    selectedLanguage = language;
    localStorage.setItem('selectedLanguage', language);
    window.location.href = 'form.html';
}

function goBack() {
    window.location.href = 'index.html';
}

function goToForm() {
    window.location.href = 'form.html';
}

// Load language on form page
window.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage === 'form.html') {
        selectedLanguage = localStorage.getItem('selectedLanguage') || 'English';
        applyTranslations();
        setupFormSubmission();
    } else if (currentPage === 'results.html') {
        selectedLanguage = localStorage.getItem('selectedLanguage') || 'English';
        applyTranslations();
        fetchResults();
    }
});

function applyTranslations() {
    const t = translations[selectedLanguage];
    
    // Form page translations - Labels
    const formTitle = document.getElementById('form-title');
    if (formTitle) formTitle.textContent = t.formTitle;
    
    const formSubtitle = document.getElementById('form-subtitle');
    if (formSubtitle) formSubtitle.textContent = t.formSubtitle;
    
    const labelName = document.getElementById('label-name');
    if (labelName) labelName.textContent = t.labelName;
    
    const labelAge = document.getElementById('label-age');
    if (labelAge) labelAge.textContent = t.labelAge;
    
    const labelGender = document.getElementById('label-gender');
    if (labelGender) labelGender.textContent = t.labelGender;
    
    const labelState = document.getElementById('label-state');
    if (labelState) labelState.textContent = t.labelState;
    
    const labelCategory = document.getElementById('label-category');
    if (labelCategory) labelCategory.textContent = t.labelCategory;
    
    const labelCommunity = document.getElementById('label-community');
    if (labelCommunity) labelCommunity.textContent = t.labelCommunity;
    
    const labelPhysicallyChallenged = document.getElementById('label-physically-challenged');
    if (labelPhysicallyChallenged) labelPhysicallyChallenged.textContent = t.labelPhysicallyChallenged;
    
    const labelQuery = document.getElementById('label-query');
    if (labelQuery) labelQuery.textContent = t.labelQuery;
    
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.textContent = t.submitBtn;
    
    // Populate State dropdown with translations
    const stateSelect = document.getElementById('state');
    if (stateSelect && t.states) {
        const currentValue = stateSelect.value;
        stateSelect.innerHTML = `<option value="">${t.statePlaceholder}</option>`;
        for (const [key, value] of Object.entries(t.states)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            stateSelect.appendChild(option);
        }
        stateSelect.value = currentValue;
    }
    
    // Populate Category dropdown with translations
    const categorySelect = document.getElementById('category');
    if (categorySelect && t.categories) {
        const currentValue = categorySelect.value;
        categorySelect.innerHTML = `<option value="">${t.categoryPlaceholder}</option>`;
        for (const [key, value] of Object.entries(t.categories)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            categorySelect.appendChild(option);
        }
        categorySelect.value = currentValue;
    }
    
    // Populate Gender dropdown with translations
    const genderSelect = document.getElementById('gender');
    if (genderSelect && t.genderOptions) {
        const currentValue = genderSelect.value;
        genderSelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.genderOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            genderSelect.appendChild(option);
        }
        genderSelect.value = currentValue;
    }
    
    // Populate Community dropdown with translations
    const communitySelect = document.getElementById('community');
    if (communitySelect && t.communityOptions) {
        const currentValue = communitySelect.value;
        communitySelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.communityOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            communitySelect.appendChild(option);
        }
        communitySelect.value = currentValue;
    }
    
    // Populate Physically Challenged dropdown with translations
    const physicallyChallengedSelect = document.getElementById('physically_challenged');
    if (physicallyChallengedSelect && t.physicallyChallengedOptions) {
        const currentValue = physicallyChallengedSelect.value;
        physicallyChallengedSelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.physicallyChallengedOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            physicallyChallengedSelect.appendChild(option);
        }
        physicallyChallengedSelect.value = currentValue;
    }
    
    // Results page translations
    const resultsTitle = document.getElementById('results-title');
    if (resultsTitle) resultsTitle.textContent = t.resultsTitle;
}

function setupFormSubmission() {
    const form = document.getElementById('scheme-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            state: document.getElementById('state').value,
            category: document.getElementById('category').value,
            community: document.getElementById('community').value,
            physically_challenged: document.getElementById('physically_challenged').value,
            language: languageCodes[selectedLanguage] || 'en',
            query: document.getElementById('query').value
        };
        
        // Store form data for results page
        localStorage.setItem('formData', JSON.stringify(formData));
        
        // Navigate to results page
        window.location.href = 'results.html';
    });
}

async function fetchResults() {
    const formData = JSON.parse(localStorage.getItem('formData'));
    
    if (!formData) {
        window.location.href = 'form.html';
        return;
    }
    
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }
        
        const data = await response.json();
        
        // Hide loading, show results
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
        
        // Display response
        document.getElementById('response-text').innerHTML = formatResponse(data.response);
        
        // Display sources
        if (data.sources && data.sources.length > 0) {
            document.getElementById('sources-section').style.display = 'block';
            const sourcesList = document.getElementById('sources-list');
            sourcesList.innerHTML = data.sources.map(s => 
                `<li>${s.source} (Chunk ${s.chunk_id})</li>`
            ).join('');
        }
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').style.display = 'block';
        document.getElementById('error-message').textContent = 
            'Sorry, we encountered an error. Please try again.';
    }
}

function formatResponse(text) {
    // Convert markdown to HTML
    return text
        .replace(/### (.*?)(\n|$)/g, '<h3>$1</h3>')
        .replace(/## (.*?)(\n|$)/g, '<h2>$1</h2>')
        .replace(/# (.*?)(\n|$)/g, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function downloadPDF() {
    const alertMessage = 'PDF export feature coming soon!';
    const customTitle = 'AICloud for Bharat';
    
    // Create custom alert dialog
    const dialog = document.createElement('div');
    dialog.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:2px solid #333;border-radius:8px;box-shadow:0 4px 6px rgba(0,0,0,0.3);z-index:10000;text-align:center;';
    dialog.innerHTML = `
        <h3 style="margin:0 0 15px 0;color:#333;">${customTitle}</h3>
        <p style="margin:0 0 15px 0;">${alertMessage}</p>
        <button onclick="this.parentElement.remove();document.getElementById('overlay').remove();" style="padding:8px 20px;background:#007bff;color:white;border:none;border-radius:4px;cursor:pointer;">OK</button>
    `;
    
    const overlay = document.createElement('div');
    overlay.id = 'overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;';
    overlay.onclick = () => { dialog.remove(); overlay.remove(); };
    
    document.body.appendChild(overlay);
    document.body.appendChild(dialog);
}