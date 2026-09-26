/**
 * ===================================================================
 *  Smart Crop Recommendation System — Main JavaScript
 *  Handles: form submission, API calls, result rendering, UI effects
 * ===================================================================
 */

// ---------------------------------------------------------------------------
//  DOM Elements
// ---------------------------------------------------------------------------
const navbar       = document.getElementById('navbar');
const hamburger    = document.getElementById('hamburger');
const navLinks     = document.getElementById('nav-links');
const scrollTopBtn = document.getElementById('scroll-top');
const cropForm     = document.getElementById('crop-form');

// Result card elements
const resultPlaceholder = document.getElementById('result-placeholder');
const spinner           = document.getElementById('spinner');
const resultDisplay     = document.getElementById('result-display');
const resultError       = document.getElementById('result-error');
const btnRetry          = document.getElementById('btn-retry');
const btnPredict        = document.getElementById('btn-predict');

// ---------------------------------------------------------------------------
//  Navbar scroll effect
// ---------------------------------------------------------------------------
window.addEventListener('scroll', () => {
    // Add 'scrolled' class when user scrolls down
    if (window.scrollY > 60) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }

    // Show/hide scroll-to-top button
    if (window.scrollY > 400) {
        scrollTopBtn.classList.add('visible');
    } else {
        scrollTopBtn.classList.remove('visible');
    }
});

// ---------------------------------------------------------------------------
//  Mobile hamburger menu toggle
// ---------------------------------------------------------------------------
hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
});

// Close menu when a link is clicked
navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('open');
    });
});

// ---------------------------------------------------------------------------
//  Scroll-to-top button
// ---------------------------------------------------------------------------
scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ---------------------------------------------------------------------------
//  Hero floating particles
// ---------------------------------------------------------------------------
function createParticles() {
    const container = document.getElementById('hero-particles');
    if (!container) return;

    const particleCount = 25;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('hero-particle');

        // Random size, position, and animation duration
        const size = Math.random() * 6 + 2;
        particle.style.width  = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left   = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 12 + 8) + 's';
        particle.style.animationDelay    = (Math.random() * 10) + 's';

        // Random color between green and cyan
        const hue = Math.random() > 0.5 ? '142' : '186';
        particle.style.background = `hsl(${hue}, 70%, 60%)`;

        container.appendChild(particle);
    }
}
createParticles();

// ---------------------------------------------------------------------------
//  Input Validation Helpers
// ---------------------------------------------------------------------------

/**
 * Validate a single numeric input field.
 * @param {string} id    - Input element ID (e.g., 'input-n')
 * @param {string} name  - Human-readable name (e.g., 'Nitrogen')
 * @param {number} min   - Minimum allowed value
 * @param {number} max   - Maximum allowed value
 * @returns {number|null} - Parsed value or null if invalid
 */
function validateNumericField(id, name, min, max) {
    const input   = document.getElementById(id);
    const errorEl = document.getElementById('error-' + id.split('-')[1]);
    const value   = input.value.trim();

    // Clear previous error
    input.classList.remove('input-error-state');
    if (errorEl) errorEl.textContent = '';

    // Check empty
    if (value === '') {
        input.classList.add('input-error-state');
        if (errorEl) errorEl.textContent = `${name} is required.`;
        return null;
    }

    // Check numeric
    const num = parseFloat(value);
    if (isNaN(num)) {
        input.classList.add('input-error-state');
        if (errorEl) errorEl.textContent = `Enter a valid number.`;
        return null;
    }

    // Check range
    if (num < min || num > max) {
        input.classList.add('input-error-state');
        if (errorEl) errorEl.textContent = `Must be between ${min} and ${max}.`;
        return null;
    }

    return num;
}

/**
 * Validate the city name input.
 * @returns {string|null} - Trimmed city name or null if invalid
 */
function validateCity() {
    const input   = document.getElementById('input-city');
    const errorEl = document.getElementById('error-city');
    const value   = input.value.trim();

    input.classList.remove('input-error-state');
    if (errorEl) errorEl.textContent = '';

    if (value === '' || value.length < 2) {
        input.classList.add('input-error-state');
        if (errorEl) errorEl.textContent = 'Enter a valid city name.';
        return null;
    }

    return value;
}

// ---------------------------------------------------------------------------
//  Show / Hide Result States
// ---------------------------------------------------------------------------
function showState(state) {
    // Hide all states first
    resultPlaceholder.style.display = 'none';
    spinner.style.display           = 'none';
    resultDisplay.style.display     = 'none';
    resultError.style.display       = 'none';

    // Show the requested state
    switch (state) {
        case 'placeholder':
            resultPlaceholder.style.display = 'block';
            break;
        case 'loading':
            spinner.style.display = 'flex';
            break;
        case 'result':
            resultDisplay.style.display = 'block';
            break;
        case 'error':
            resultError.style.display = 'block';
            break;
    }
}

// ---------------------------------------------------------------------------
//  Toast Notification
// ---------------------------------------------------------------------------
function showToast(message, icon = '✅') {
    const toast     = document.getElementById('toast');
    const toastMsg  = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    toastMsg.textContent  = message;
    toastIcon.textContent = icon;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

// ---------------------------------------------------------------------------
//  Render Prediction Result
// ---------------------------------------------------------------------------
function renderResult(data) {
    // Crop icon and name
    document.getElementById('result-icon').textContent      = data.emoji || '🌾';
    document.getElementById('result-crop-name').textContent  = data.crop;

    // Confidence bar animation
    const confidenceFill  = document.getElementById('confidence-fill');
    const confidenceValue = document.getElementById('confidence-value');
    confidenceValue.textContent = data.confidence + '%';
    // Animate the bar after a short delay
    setTimeout(() => {
        confidenceFill.style.width = data.confidence + '%';
    }, 100);

    // ★ Suitability message — clear and beginner-friendly
    document.getElementById('result-message').textContent = 
        `Based on soil and weather conditions in ${data.weather.city}, ` +
        `this crop is suitable for your region. ` +
        `Our AI model recommends growing ${data.crop} with ${data.confidence}% confidence.`;

    // ★ Prominent weather display — Temperature and Humidity shown clearly
    const weatherCard = document.getElementById('weather-display-card');
    weatherCard.style.display = 'block';
    document.getElementById('wi-city').textContent      = data.weather.city;
    document.getElementById('wi-temp').textContent      = data.weather.temperature + '°C';
    document.getElementById('wi-humidity').textContent   = data.weather.humidity + '%';
    document.getElementById('wi-desc').textContent      = data.weather.description;

    // If demo mode, add a note
    if (data.weather.demo) {
        document.getElementById('wi-desc').textContent += ' (Demo mode — add your API key)';
    }

    // Result tags
    const tagsContainer = document.getElementById('result-tags');
    tagsContainer.innerHTML = '';

    const tags = [
        { icon: 'fa-calendar-alt',     text: `Season: ${data.season}` },
        { icon: 'fa-tint',             text: `Water Need: ${data.water_need}` },
        { icon: 'fa-percentage',       text: `Confidence: ${data.confidence}%` },
        { icon: 'fa-thermometer-half', text: `Temperature: ${data.weather.temperature}°C` },
        { icon: 'fa-droplet',          text: `Humidity: ${data.weather.humidity}%` },
    ];

    tags.forEach(tag => {
        const el = document.createElement('span');
        el.className = 'result-tag';
        el.innerHTML = `<i class="fas ${tag.icon}"></i> ${tag.text}`;
        tagsContainer.appendChild(el);
    });

    // Show result state
    showState('result');

    // Scroll result card into view
    document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Success toast
    showToast(`Recommended: ${data.crop} (${data.confidence}%)`, data.emoji || '🌾');
}

// ---------------------------------------------------------------------------
//  Show Error — with specific titles for weather/input errors
// ---------------------------------------------------------------------------
function renderError(message) {
    const errorTitle = document.getElementById('error-title');
    const errorHint  = document.getElementById('error-hint');

    document.getElementById('error-message').textContent = message;

    // Detect weather-related errors and show specific messaging
    if (message.toLowerCase().includes('weather') || message.toLowerCase().includes('city')) {
        errorTitle.textContent = 'Unable to Fetch Weather Data';
        errorHint.textContent  = 'Please check the city name and your internet connection, then try again.';
    } else if (message.toLowerCase().includes('model') || message.toLowerCase().includes('train')) {
        errorTitle.textContent = 'ML Model Not Ready';
        errorHint.textContent  = 'Run "python train_model.py" to train the model first.';
    } else if (message.toLowerCase().includes('connect') || message.toLowerCase().includes('server')) {
        errorTitle.textContent = 'Server Connection Failed';
        errorHint.textContent  = 'Make sure Flask is running on localhost:5000.';
    } else {
        errorTitle.textContent = 'Something Went Wrong';
        errorHint.textContent  = 'Please check your inputs and try again.';
    }

    showState('error');
    showToast('Prediction failed — see error details.', '⚠️');
}

// ---------------------------------------------------------------------------
//  Form Submission Handler
// ---------------------------------------------------------------------------
cropForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Reset confidence bar
    document.getElementById('confidence-fill').style.width = '0%';

    // Validate all fields
    const n    = validateNumericField('input-n',  'Nitrogen (N)',   0, 200);
    const p    = validateNumericField('input-p',  'Phosphorus (P)', 0, 200);
    const k    = validateNumericField('input-k',  'Potassium (K)',  0, 200);
    const ph   = validateNumericField('input-ph', 'pH Value',       0, 14);
    const city = validateCity();

    // If any field is invalid, stop
    if (n === null || p === null || k === null || ph === null || city === null) {
        showToast('Please fix the errors in the form.', '⚠️');
        return;
    }

    // Show loading state
    showState('loading');
    btnPredict.disabled = true;
    btnPredict.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Predicting…';

    try {
        // Send POST request to Flask /predict endpoint
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                N: n,
                P: p,
                K: k,
                ph: ph,
                city: city
            })
        });

        const result = await response.json();

        if (result.success) {
            // Render the prediction result
            renderResult(result);
        } else {
            // Show error from backend
            renderError(result.error || 'An unknown error occurred.');
        }

    } catch (error) {
        // Network error or server unreachable
        console.error('Prediction error:', error);
        renderError('Could not connect to the server. Make sure Flask is running on localhost:5000.');
    } finally {
        // Re-enable button
        btnPredict.disabled = false;
        btnPredict.innerHTML = '<i class="fas fa-search"></i> Predict Best Crop';
    }
});

// ---------------------------------------------------------------------------
//  Retry Button
// ---------------------------------------------------------------------------
btnRetry.addEventListener('click', () => {
    showState('placeholder');
    // Scroll to form
    document.getElementById('recommend').scrollIntoView({ behavior: 'smooth' });
});

// ---------------------------------------------------------------------------
//  Animate elements on scroll (Intersection Observer)
// ---------------------------------------------------------------------------
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -60px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity   = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Select elements to animate
    const animatedElements = document.querySelectorAll(
        '.feature-card, .step-card, .tech-card'
    );

    animatedElements.forEach((el, index) => {
        el.style.opacity    = '0';
        el.style.transform  = 'translateY(30px)';
        el.style.transition = `all 0.6s cubic-bezier(.4,0,.2,1) ${index * 0.08}s`;
        observer.observe(el);
    });
}
setupScrollAnimations();

// ---------------------------------------------------------------------------
//  Real-time validation on input blur (validates as user tabs between fields)
// ---------------------------------------------------------------------------
document.getElementById('input-n').addEventListener('blur', () => {
    validateNumericField('input-n', 'Nitrogen (N)', 0, 200);
});
document.getElementById('input-p').addEventListener('blur', () => {
    validateNumericField('input-p', 'Phosphorus (P)', 0, 200);
});
document.getElementById('input-k').addEventListener('blur', () => {
    validateNumericField('input-k', 'Potassium (K)', 0, 200);
});
document.getElementById('input-ph').addEventListener('blur', () => {
    validateNumericField('input-ph', 'pH Value', 0, 14);
});
document.getElementById('input-city').addEventListener('blur', () => {
    validateCity();
});

// Clear error styling when user starts typing again
document.querySelectorAll('#crop-form input').forEach(input => {
    input.addEventListener('input', () => {
        input.classList.remove('input-error-state');
        const errorId = 'error-' + input.id.split('-')[1];
        const errorEl = document.getElementById(errorId);
        if (errorEl) errorEl.textContent = '';
    });
});

// ---------------------------------------------------------------------------
//  Smooth scroll for anchor links
// ---------------------------------------------------------------------------
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ---------------------------------------------------------------------------
//  Console welcome message
// ---------------------------------------------------------------------------
console.log(
    '%c🌱 AI Smart Crop Advisor',
    'color: #22c55e; font-size: 18px; font-weight: bold;'
);
console.log(
    '%cPowered by Random Forest ML + OpenWeatherMap API',
    'color: #06b6d4; font-size: 12px;'
);
