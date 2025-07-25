// Main JavaScript file for KrishiMitra
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeComponents();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize dark mode
    initializeDarkMode();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
});

// Initialize all components
function initializeComponents() {
    // Initialize Bootstrap components
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Initialize custom dropdowns
    initializeDropdowns();
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize form validation
    initializeFormValidation();
}

// Set up event listeners
function setupEventListeners() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-chip');
    filterButtons.forEach(button => {
        button.addEventListener('click', handleFilterClick);
    });
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

// Initialize dark mode
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        if (darkModeToggle) {
            darkModeToggle.checked = true;
        }
    }
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', this.checked);
            
            // Animate the transition
            document.body.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }
}

// Initialize tooltips
function initializeTooltips() {
    // Custom tooltip implementation
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

// Initialize modals
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    // Close modals on outside click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            hideModal(e.target);
        }
    });
    
    // Close modals on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                hideModal(openModal);
            }
        }
    });
}

// Initialize custom dropdowns
function initializeDropdowns() {
    const dropdownTriggers = document.querySelectorAll('.dropdown-trigger');
    dropdownTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            if (dropdown && dropdown.classList.contains('dropdown-menu')) {
                dropdown.classList.toggle('show');
            }
        });
    });
    
    // Close dropdowns on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Initialize loading states
function initializeLoadingStates() {
    const loadingButtons = document.querySelectorAll('.btn-loading');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            showButtonLoading(this);
        });
    });
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidation);
    });
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Event handlers
function toggleMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.querySelector('.mobile-menu-overlay');
    
    if (mobileMenu && overlay) {
        mobileMenu.classList.toggle('active');
        overlay.classList.toggle('active');
        document.body.classList.toggle('menu-open');
    }
}

function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const searchResults = document.querySelector('.search-results');
    
    if (searchTerm.length > 2) {
        // Simulate search API call
        showSearchResults(searchTerm);
    } else {
        hideSearchResults();
    }
}

function handleFilterClick(e) {
    const filter = e.target;
    const filterGroup = filter.closest('.filter-group');
    const filterValue = filter.getAttribute('data-filter');
    
    // Remove active class from siblings
    if (filterGroup) {
        filterGroup.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('active');
        });
    }
    
    // Add active class to clicked filter
    filter.classList.add('active');
    
    // Apply filter
    applyFilter(filterValue);
}

function handleFormSubmit(e) {
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        showButtonLoading(submitButton);
    }
    
    // Add form-specific validation
    if (form.classList.contains('otp-form')) {
        validateOTPForm(form, e);
    }
}

// Modal functions
function showModal(modal) {
    modal.classList.add('show');
    modal.style.display = 'block';
    document.body.classList.add('modal-open');
    
    // Focus first input
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) {
        firstInput.focus();
    }
}

function hideModal(modal) {
    modal.classList.remove('show');
    modal.style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Tooltip functions
function showTooltip(e) {
    const element = e.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (tooltipText) {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        element._tooltip = tooltip;
        
        setTimeout(() => {
            tooltip.classList.add('show');
        }, 10);
    }
}

function hideTooltip(e) {
    const element = e.target;
    if (element._tooltip) {
        element._tooltip.remove();
        element._tooltip = null;
    }
}

// Loading functions
function showButtonLoading(button) {
    const originalText = button.textContent;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    button.disabled = true;
}

function hideButtonLoading(button) {
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.textContent = originalText;
        button.removeAttribute('data-original-text');
    }
    button.disabled = false;
}

// Validation functions
function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    
    if (input.hasAttribute('required') && !value) {
        showInputError(input, 'This field is required');
        return false;
    }
    
    if (input.type === 'email' && value && !isValidEmail(value)) {
        showInputError(input, 'Please enter a valid email address');
        return false;
    }
    
    if (input.type === 'tel' && value && !isValidPhone(value)) {
        showInputError(input, 'Please enter a valid phone number');
        return false;
    }
    
    clearInputError(input);
    return true;
}

function clearValidation(e) {
    const input = e.target;
    clearInputError(input);
}

function showInputError(input, message) {
    const errorElement = input.parentElement.querySelector('.error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        error.style.color = '#dc3545';
        error.style.fontSize = '0.875rem';
        error.style.marginTop = '0.25rem';
        input.parentElement.appendChild(error);
    }
    
    input.classList.add('is-invalid');
}

function clearInputError(input) {
    const errorElement = input.parentElement.querySelector('.error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
    input.classList.remove('is-invalid');
}

function validateOTPForm(form, e) {
    const otpInput = form.querySelector('input[name="otp"]');
    if (otpInput) {
        const otpValue = otpInput.value.trim();
        if (otpValue.length !== 6 || !/^\d{6}$/.test(otpValue)) {
            e.preventDefault();
            showInputError(otpInput, 'Please enter a valid 6-digit OTP');
        }
    }
}

// Search functions
function showSearchResults(searchTerm) {
    // This would typically make an API call
    console.log('Searching for:', searchTerm);
    
    // Simulate search results
    const results = [
        { title: 'Fresh Tomatoes', category: 'Vegetables' },
        { title: 'Organic Rice', category: 'Grains' },
        { title: 'Premium Wheat', category: 'Grains' }
    ].filter(item => item.title.toLowerCase().includes(searchTerm));
    
    displaySearchResults(results);
}

function displaySearchResults(results) {
    let searchResultsContainer = document.querySelector('.search-results');
    
    if (!searchResultsContainer) {
        searchResultsContainer = document.createElement('div');
        searchResultsContainer.className = 'search-results';
        searchResultsContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            max-height: 300px;
            overflow-y: auto;
        `;
        
        const searchContainer = document.querySelector('.search-bar');
        if (searchContainer) {
            searchContainer.style.position = 'relative';
            searchContainer.appendChild(searchResultsContainer);
        }
    }
    
    if (results.length > 0) {
        searchResultsContainer.innerHTML = results.map(result => `
            <div class="search-result-item" style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer;">
                <div style="font-weight: 500;">${result.title}</div>
                <div style="color: #666; font-size: 0.875rem;">${result.category}</div>
            </div>
        `).join('');
        
        searchResultsContainer.style.display = 'block';
    } else {
        searchResultsContainer.innerHTML = '<div style="padding: 12px; text-align: center; color: #666;">No results found</div>';
        searchResultsContainer.style.display = 'block';
    }
}

function hideSearchResults() {
    const searchResultsContainer = document.querySelector('.search-results');
    if (searchResultsContainer) {
        searchResultsContainer.style.display = 'none';
    }
}

// Filter functions
function applyFilter(filterValue) {
    const items = document.querySelectorAll('[data-filter-target]');
    
    items.forEach(item => {
        const itemCategories = item.getAttribute('data-filter-target').split(',');
        
        if (filterValue === 'all' || itemCategories.includes(filterValue)) {
            item.style.display = 'block';
            item.classList.add('fade-in');
        } else {
            item.style.display = 'none';
            item.classList.remove('fade-in');
        }
    });
}

// Utility validation functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[+]?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

// Notification functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1050;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1;">${message}</div>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 18px; cursor: pointer;">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Export functions for use in other files
window.KrishiMitra = {
    showNotification,
    showButtonLoading,
    hideButtonLoading,
    validateInput,
    debounce,
    throttle
};
