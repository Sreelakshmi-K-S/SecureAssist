document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn');
    const scanCurrentBtn = document.getElementById('scan-current-btn');
    const backBtn = document.getElementById('back-btn');
    const inputField = document.getElementById('target-input');
    
    // View containers
    const viewInput = document.getElementById('view-input');
    const viewResult = document.getElementById('view-result');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-msg');
    
    // Action: Scan Manual Input
    scanBtn.addEventListener('click', () => {
        const text = inputField.value.trim();
        if (text) {
            analyzeTarget(text);
        } else {
            showError("Please enter a URL or message.");
        }
    });
    
    // Action: Scan Current Tab
    scanCurrentBtn.addEventListener('click', () => {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs && tabs[0] && tabs[0].url) {
                const url = tabs[0].url;
                if (url.startsWith('http')) {
                    inputField.value = url;
                    analyzeTarget(url);
                } else {
                    showError("Cannot scan internal browser pages or invalid URLs.");
                }
            } else {
                showError("Could not retrieve current tab URL.");
            }
        });
    });
    
    // Action: Go Back
    backBtn.addEventListener('click', () => {
        viewResult.classList.add('hidden');
        viewInput.classList.remove('hidden');
        inputField.value = '';
    });
    
    // API Call
    async function analyzeTarget(input) {
        errorMsg.classList.add('hidden');
        scanBtn.disabled = true;
        scanCurrentBtn.disabled = true;
        loading.classList.remove('hidden');
        
        try {
            // Point to local server (Assumes server is running)
            const response = await fetch('http://127.0.0.1:7860/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: input })
            });
            
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }
            
            const data = await response.json();
            displayResult(data);
        } catch (error) {
            showError(`Analysis failed: Ensure the SecureAssist app is running. (${error.message})`);
        } finally {
            scanBtn.disabled = false;
            scanCurrentBtn.disabled = false;
            loading.classList.add('hidden');
        }
    }
    
    // Render Results
    function displayResult(data) {
        viewInput.classList.add('hidden');
        viewResult.classList.remove('hidden');
        
        // Define styles base on score
        let styleClass = 'safe';
        let label = 'SECURED';
        if (data.score >= 70) { styleClass = 'threat'; label = 'THREAT DETECTED'; }
        else if (data.score >= 30) { styleClass = 'warn'; label = 'SUSPICIOUS'; }
        
        // Update Badge
        const badge = document.getElementById('result-badge');
        badge.className = `badge ${styleClass}`;
        badge.textContent = label;
        
        // Update Score
        const scoreVal = document.getElementById('result-score');
        scoreVal.className = `score-val ${styleClass}`;
        scoreVal.textContent = data.score;
        
        // Update Advice
        document.getElementById('result-advice').textContent = data.advice;
        
        // Render Reasons (Threat Indicators)
        const reasonsContainer = document.getElementById('result-reasons');
        reasonsContainer.innerHTML = '';
        
        if (data.reasons && data.reasons.length > 0) {
            data.reasons.forEach(r => {
                const el = document.createElement('div');
                el.className = 'reason-item';
                if (r.toUpperCase().includes('CRITICAL')) el.classList.add('critical');
                const textNode = document.createTextNode(r);
                el.appendChild(textNode);
                reasonsContainer.appendChild(el);
            });
        } else {
            const el = document.createElement('div');
            el.className = 'reason-item';
            el.style.color = '#16a34a';
            el.textContent = "✓ No threat indicators detected.";
            reasonsContainer.appendChild(el);
        }
    }
    
    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }
});
