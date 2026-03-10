// Modern interactive UI with animations
document.addEventListener('DOMContentLoaded', function () {
    // Animate risk score counter (only on results page)
    const riskValue = document.querySelector('.risk-value');
    if (riskValue) {
        const finalScore = parseInt(riskValue.textContent);
        let currentScore = 0;
        const increment = finalScore / 50;
        
        riskValue.textContent = '0';
        
        const counter = setInterval(() => {
            currentScore += increment;
            if (currentScore >= finalScore) {
                currentScore = finalScore;
                clearInterval(counter);
            }
            riskValue.textContent = Math.floor(currentScore);
        }, 30);
    }

    // Form handling - Add loading state
    const form = document.querySelector('#analyzeForm');
    const submitBtn = form ? form.querySelector('.btn-primary') : null;

    if (form && submitBtn) {
        form.addEventListener('submit', function () {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
        });

        // Re-enable button on page load (in case of back button)
        window.addEventListener('pageshow', () => {
            if (submitBtn && submitBtn.disabled) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Analyze';
            }
        });
    }

    // Add hover effect to stat items
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach((item, index) => {
        item.style.animationDelay = `${0.1 + index * 0.1}s`;
    });

    // Stagger animation for reason items
    const reasonItems = document.querySelectorAll('.reasons-list li');
    reasonItems.forEach((item, index) => {
        item.style.animationDelay = `${0.1 + index * 0.1}s`;
    });

    // Keyboard shortcut: Ctrl/Cmd + Enter to submit
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const form = document.querySelector('#analyzeForm');
            if (form) {
                form.submit();
            }
        }
    });

    // Auto-focus on input field (only on home page)
    const inputField = document.querySelector('.input-field');
    if (inputField && inputField.placeholder.includes('Paste')) {
        inputField.focus();
    }

    // Scroll into view for results (on results page)
    const resultsSection = document.querySelector('.results-section');
    if (resultsSection) {
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    // Add smooth scroll behavior for links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
