// PCOS Web Application - Enhanced User Experience

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all components
    initializeFormValidation();
    initializeNavigation();
    initializeAnimations();
    initializeAccessibility();
    
    console.log('PCOS Web Application loaded successfully!');
});

// Form validation and enhancement
function initializeFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input[type="number"]');
    
    inputs.forEach(input => {
        // Add real-time validation
        input.addEventListener('input', function() {
            validateInput(this);
        });
        
        // Add focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            validateInput(this);
        });
    });
    
    // Form submission handling
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            showMessage('Please correct the errors before submitting.', 'error');
        } else {
            showLoadingState();
        }
    });
}

// Input validation
function validateInput(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.getAttribute('min'));
    const max = parseFloat(input.getAttribute('max'));
    
    // Remove existing error states
    input.classList.remove('error', 'valid');
    const errorElement = input.parentElement.querySelector('.error-message');
    if (errorElement) errorElement.remove();
    
    // Validate range
    if (input.value !== '' && (value < min || value > max)) {
        input.classList.add('error');
        showInputError(input, `Value must be between ${min} and ${max}`);
        return false;
    }
    
    // Validate required fields
    if (input.hasAttribute('required') && input.value === '') {
        input.classList.add('error');
        showInputError(input, 'This field is required');
        return false;
    }
    
    if (input.value !== '') {
        input.classList.add('valid');
    }
    
    return true;
}

// Show input error message
function showInputError(input, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#e74c3c';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '5px';
    
    input.parentElement.appendChild(errorDiv);
}

// Form validation
function validateForm() {
    const inputs = document.querySelectorAll('form input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Loading state for submit button
function showLoadingState() {
    const submitBtn = document.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.textContent = 'Processing...';
        
        // Re-enable after a delay (simulating processing)
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.innerHTML = '<i class="fas fa-search"></i> Predict PCOS Risk';
        }, 2000);
    }
}

// Navigation enhancement
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        // Set active state
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
        
        // Add hover effects
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Animation initialization
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.content-section, .info-card, .form-category');
    animateElements.forEach(el => observer.observe(el));
    
    // Add CSS animation classes
    const style = document.createElement('style');
    style.textContent = `
        .content-section, .info-card, .form-category {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .animate-in {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);
}

// Accessibility features
function initializeAccessibility() {
    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: #667eea;
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID
    const mainContent = document.querySelector('.main-content') || document.querySelector('.container');
    if (mainContent) {
        mainContent.id = 'main-content';
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals or reset form
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement.tagName === 'INPUT') {
                activeElement.blur();
            }
        }
        
        // Enter key on form elements
        if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
            const form = e.target.closest('form');
            if (form) {
                e.preventDefault();
                form.submit();
            }
        }
    });
}

// Message display system
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${getMessageIcon(type)}"></i>
        <span>${message}</span>
        <button class="close-btn" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Style the close button
    const closeBtn = messageDiv.querySelector('.close-btn');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        margin-left: auto;
        padding: 0;
        font-size: 1.1rem;
    `;
    
    // Insert message at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 5000);
}

// Get appropriate icon for message type
function getMessageIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize smooth scrolling
initializeSmoothScrolling();

// Export functions for global access
window.PCOSApp = {
    showMessage,
    validateForm,
    validateInput
};
