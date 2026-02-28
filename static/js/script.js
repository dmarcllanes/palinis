// ─── Mobile Navigation ───────────────────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');

if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('open');
        hamburger.classList.toggle('open', isOpen);
        hamburger.setAttribute('aria-expanded', String(isOpen));
    });

    // Close menu when any nav link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            hamburger.classList.remove('open');
            hamburger.setAttribute('aria-expanded', 'false');
        });
    });

    // Close menu on outside click
    document.addEventListener('click', e => {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('open');
            hamburger.classList.remove('open');
            hamburger.setAttribute('aria-expanded', 'false');
        }
    });
}

// ─── Navbar shadow and blur on scroll ──────────────────────────────────────
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    if (!navbar) return;
    if (window.scrollY > 20) {
        navbar.style.boxShadow = '0 10px 30px -10px rgba(0,0,0,0.1)';
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
    } else {
        navbar.style.boxShadow = 'none';
        navbar.style.background = 'rgba(255, 255, 255, 0.9)';
    }
}, { passive: true });

// ─── Number Animation Logic ──────────────────────────────────────────────────
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // Easing function for smoother stop
        const easeOutQuad = 1 - (1 - progress) * (1 - progress);

        let currentVal = Math.floor(progress * (end - start) + start);
        obj.innerHTML = '$' + currentVal;

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = '$' + end;
        }
    };
    window.requestAnimationFrame(step);
}

// ─── Quote Calculator ────────────────────────────────────────────────────────
const basePrices = {
    regular: { 1: 89, 2: 135, 3: 165, 4: 195, 5: 225 },
    deep: { 1: 149, 2: 189, 3: 245, 4: 299, 5: 349 },
    endlease: { 1: 199, 2: 299, 3: 399, 4: 499, 5: 599 },
};

const bathroomMultipliers = { 1: 1.0, 2: 1.15, 3: 1.3, 4: 1.45 };
const addOnPrices = { oven: 35, carpet: 50, balcony: 25, windows: 40 };

let currentPrice = 195; // Initial hardcoded view

window.updateQuote = function () {
    const bedroomsElement = document.getElementById('bedrooms');
    const bathroomsElement = document.getElementById('bathrooms');
    const serviceTypeElement = document.getElementById('service-type');

    // Safety check just in case DOM isn't fully ready
    if (!bedroomsElement || !bathroomsElement || !serviceTypeElement) return;

    const bedrooms = bedroomsElement.value;
    const bathrooms = bathroomsElement.value;
    const serviceType = serviceTypeElement.value;

    let targetPrice = basePrices[serviceType][bedrooms] * bathroomMultipliers[bathrooms];

    document.querySelectorAll('.addon-item input[type="checkbox"]:checked').forEach(cb => {
        targetPrice += addOnPrices[cb.value] || 0;
    });

    targetPrice = Math.round(targetPrice);

    const priceElement = document.getElementById('price-value');
    if (priceElement && currentPrice !== targetPrice) {
        animateValue(priceElement, currentPrice, targetPrice, 500);
        currentPrice = targetPrice;
    }
}

// ─── Advanced Scroll Reveal Animation ─────────────────────────────────────────
const observerOptions = {
    root: null,
    rootMargin: '0px 0px -100px 0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            // Add a small stagger delay based on DOM order for grid items
            setTimeout(() => {
                entry.target.classList.add('visible');
            }, (index % 4) * 100);

            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    // Collect elements to animate
    const animateTargets = document.querySelectorAll(
        '.service-card, .review-card, .step, .plan, .benefit, .hero-content, .calculator, .how-it-works h2'
    );

    animateTargets.forEach(el => {
        el.classList.add('fade-up');
        observer.observe(el);
    });

    // Run initial quote calculation safely
    updateQuote();
});

// ─── PWA Service Worker ──────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => { });
    });
}
