/**
 * KidneyGuard — Frontend JavaScript
 * ==================================
 * Handles form section navigation, progress bar,
 * client-side validation, and micro-animations.
 */

// ----- Form Section Navigation -----
let currentSection = 1;
const totalSections = 4;

function showSection(sectionNum) {
    // Hide all sections
    document.querySelectorAll('.form-section').forEach(s => {
        s.classList.remove('active');
    });

    // Show target section
    const target = document.querySelector(`.form-section[data-section="${sectionNum}"]`);
    if (target) {
        target.classList.add('active');
    }

    // Update progress bar
    updateProgress(sectionNum);
    currentSection = sectionNum;

    // Scroll to top of form
    window.scrollTo({ top: 200, behavior: 'smooth' });
}

function nextSection(sectionNum) {
    // Validate current section before moving forward
    if (!validateCurrentSection()) {
        return;
    }
    showSection(sectionNum);
}

function prevSection(sectionNum) {
    showSection(sectionNum);
}

function updateProgress(sectionNum) {
    // Update progress bar fill
    const progressPercent = ((sectionNum - 1) / (totalSections - 1)) * 100;
    const fill = document.querySelector('.progress-fill');
    if (fill) {
        fill.style.width = progressPercent + '%';
    }

    // Update step indicators
    document.querySelectorAll('.progress-step').forEach(step => {
        const stepNum = parseInt(step.getAttribute('data-section'));
        step.classList.remove('active', 'completed');

        if (stepNum < sectionNum) {
            step.classList.add('completed');
        } else if (stepNum === sectionNum) {
            step.classList.add('active');
        }
    });
}

// ----- Client-Side Validation -----
function validateCurrentSection() {
    const section = document.querySelector(`.form-section[data-section="${currentSection}"]`);
    if (!section) return true;

    const requiredInputs = section.querySelectorAll('input[required], select[required]');
    let isValid = true;
    let errorMessages = [];

    requiredInputs.forEach(input => {
        // Reset previous styling
        input.style.borderColor = '';

        const value = input.value.trim();

        if (!value) {
            isValid = false;
            input.style.borderColor = '#ef4444';
            const label = input.closest('.form-group')?.querySelector('label')?.textContent?.replace('*', '').trim();
            errorMessages.push(`${label || 'Field'} is required`);
        } else if (input.type === 'number') {
            const num = parseFloat(value);
            const min = parseFloat(input.min);
            const max = parseFloat(input.max);

            if (isNaN(num)) {
                isValid = false;
                input.style.borderColor = '#ef4444';
                const label = input.closest('.form-group')?.querySelector('label')?.textContent?.replace('*', '').trim();
                errorMessages.push(`${label} must be a valid number`);
            } else if (min && num < min) {
                isValid = false;
                input.style.borderColor = '#ef4444';
                const label = input.closest('.form-group')?.querySelector('label')?.textContent?.replace('*', '').trim();
                errorMessages.push(`${label} must be at least ${min}`);
            } else if (max && num > max) {
                isValid = false;
                input.style.borderColor = '#ef4444';
                const label = input.closest('.form-group')?.querySelector('label')?.textContent?.replace('*', '').trim();
                errorMessages.push(`${label} must be at most ${max}`);
            }
        }
    });

    if (!isValid) {
        showValidationToast(errorMessages[0]);
    }

    return isValid;
}

// ----- Validation Toast -----
function showValidationToast(message) {
    // Remove existing toast
    const existing = document.querySelector('.validation-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'validation-toast';
    toast.innerHTML = `<span></span><span>${message}</span>`;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(239, 68, 68, 0.95);
        color: white;
        padding: 14px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1000;
        animation: fadeInUp 0.3s ease;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
        font-family: 'Inter', sans-serif;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ----- Form Submission Validation -----
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('health-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Validate all required fields across all sections
            const requiredInputs = form.querySelectorAll('input[required], select[required]');
            let allValid = true;
            let firstError = null;

            requiredInputs.forEach(input => {
                const value = input.value.trim();
                if (!value) {
                    allValid = false;
                    input.style.borderColor = '#ef4444';
                    if (!firstError) {
                        const label = input.closest('.form-group')?.querySelector('label')?.textContent?.replace('*', '').trim();
                        firstError = `Please fill all required fields. Missing: ${label}`;
                    }
                }
            });

            if (!allValid) {
                e.preventDefault();
                showValidationToast(firstError || 'Please fill all required fields');
                return false;
            }
        });
    }

    // ----- Input Focus Animations -----
    document.querySelectorAll('.form-group input, .form-group select').forEach(input => {
        input.addEventListener('focus', function () {
            this.closest('.form-group')?.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.closest('.form-group')?.classList.remove('focused');
            // Clear error styling on valid input
            if (this.value.trim()) {
                this.style.borderColor = '';
            }
        });
    });

    // ----- Smooth Entrance Animations -----
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.step-card, .trust-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
});
