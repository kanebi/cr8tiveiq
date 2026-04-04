// Form validation and handling

class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (this.form) {
            this.init();
        }
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.setupFieldValidation();
    }

    setupFieldValidation() {
        const fields = this.form.querySelectorAll('input, textarea, select');
        
        fields.forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.validateField(field));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const name = field.name;
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = `${this.formatFieldName(name)} is required`;
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }

        // Phone validation
        if (type === 'tel' && value) {
            const phoneRegex = /^[\d\s\-\+\(\)]+$/;
            if (!phoneRegex.test(value) || value.replace(/\D/g, '').length < 10) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }

        // Minimum length validation
        if (field.hasAttribute('minlength')) {
            const minLength = parseInt(field.getAttribute('minlength'));
            if (value.length > 0 && value.length < minLength) {
                isValid = false;
                errorMessage = `${this.formatFieldName(name)} must be at least ${minLength} characters`;
            }
        }

        // Update field styling
        this.updateFieldStatus(field, isValid, errorMessage);
        return isValid;
    }

    updateFieldStatus(field, isValid, errorMessage) {
        const fieldWrapper = field.closest('.form-group') || field.parentElement;
        
        // Remove existing error message
        const existingError = fieldWrapper.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        if (!isValid) {
            field.classList.add('border-red-500');
            field.classList.remove('border-green-500');
            
            const errorEl = document.createElement('p');
            errorEl.className = 'error-message text-red-500 text-sm mt-1';
            errorEl.textContent = errorMessage;
            fieldWrapper.appendChild(errorEl);
        } else if (field.value.trim()) {
            field.classList.remove('border-red-500');
            field.classList.add('border-green-500');
        } else {
            field.classList.remove('border-red-500', 'border-green-500');
        }
    }

    handleSubmit(e) {
        e.preventDefault();

        const fields = this.form.querySelectorAll('input, textarea, select');
        let isFormValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });

        if (isFormValid) {
            this.submitForm();
        } else {
            this.showError('Please fix the errors above');
        }
    }

    submitForm() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';

        // Simulate form submission
        setTimeout(() => {
            this.showSuccess('Form submitted successfully!');
            this.form.reset();
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 1500);
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} fixed top-4 right-4 px-6 py-4 rounded-lg text-white z-50 animate-fade-in-up`;
        
        if (type === 'error') {
            notification.classList.add('bg-red-500');
        } else {
            notification.classList.add('bg-green-500');
        }

        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    formatFieldName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/\b\w/g, char => char.toUpperCase());
    }
}

// Initialize form validators
document.addEventListener('DOMContentLoaded', () => {
    // Initialize contact form
    const contactForm = new FormValidator('form[name="contact"]');
    
    // Initialize newsletter form
    const newsletterForm = new FormValidator('form[name="newsletter"]');

    // Initialize any other forms
    document.querySelectorAll('form').forEach(form => {
        if (!form.hasAttribute('data-validator-initialized')) {
            new FormValidator(`form[name="${form.name}"]`);
            form.setAttribute('data-validator-initialized', 'true');
        }
    });
});

// Real-time character counter for textareas
document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
    const maxLength = textarea.getAttribute('maxlength');
    const counter = document.createElement('p');
    counter.className = 'text-gray-400 text-sm mt-1';
    counter.textContent = `0 / ${maxLength} characters`;
    textarea.parentElement.appendChild(counter);

    textarea.addEventListener('input', () => {
        counter.textContent = `${textarea.value.length} / ${maxLength} characters`;
    });
});

// Password strength indicator
document.querySelectorAll('input[type="password"]').forEach(passwordField => {
    const strengthIndicator = document.createElement('div');
    strengthIndicator.className = 'password-strength mt-2 h-1 bg-gray-700 rounded-full overflow-hidden';
    
    const strengthBar = document.createElement('div');
    strengthBar.className = 'h-full w-0 transition-all duration-300';
    strengthIndicator.appendChild(strengthBar);
    
    passwordField.parentElement.appendChild(strengthIndicator);

    passwordField.addEventListener('input', () => {
        const strength = calculatePasswordStrength(passwordField.value);
        const width = (strength / 4) * 100;
        
        strengthBar.style.width = width + '%';
        
        if (strength === 0) {
            strengthBar.className = 'h-full w-0 transition-all duration-300';
        } else if (strength === 1) {
            strengthBar.className = 'h-full transition-all duration-300 bg-red-500';
        } else if (strength === 2) {
            strengthBar.className = 'h-full transition-all duration-300 bg-yellow-500';
        } else if (strength === 3) {
            strengthBar.className = 'h-full transition-all duration-300 bg-blue-500';
        } else {
            strengthBar.className = 'h-full transition-all duration-300 bg-green-500';
        }
    });
});

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/\d/)) strength++;
    if (password.match(/[^a-zA-Z\d]/)) strength++;
    
    return strength;
}

// Form auto-save to localStorage
document.querySelectorAll('form').forEach(form => {
    const formName = form.name || form.id;
    
    // Load saved data
    const savedData = localStorage.getItem(`form_${formName}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.value = data[fieldName];
            }
        });
    }

    // Save data on input
    form.addEventListener('input', () => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        localStorage.setItem(`form_${formName}`, JSON.stringify(data));
    });

    // Clear saved data on submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(`form_${formName}`);
    });
});
