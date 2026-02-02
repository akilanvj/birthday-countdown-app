// Configuration
const CONFIG = {
    // Smart API URL detection for different environments
    API_BASE_URL: window.location.hostname.includes('localhost') 
        ? 'http://localhost:8000/api/nextbirthday'  // Local development
        : '/api/nextbirthday'  // Production (Static Web Apps with API integration)
};

// DOM elements
const elements = {
    form: document.getElementById('birthdayForm'),
    dobInput: document.getElementById('dob'),
    errorMessage: document.getElementById('errorMessage'),
    results: document.getElementById('results'),
    loading: document.getElementById('loading'),
    calculateBtn: document.querySelector('.calculate-btn'),
    
    // Result display elements
    ageYears: document.getElementById('ageYears'),
    nextBirthdayDate: document.getElementById('nextBirthdayDate'),
    nextBirthdayDayOfWeek: document.getElementById('nextBirthdayDayOfWeek'),
    daysUntilNextBirthday: document.getElementById('daysUntilNextBirthday'),
    message: document.getElementById('message')
};

// Initialize the application
function init() {
    // Set max date to today to prevent future dates
    const today = new Date().toISOString().split('T')[0];
    elements.dobInput.setAttribute('max', today);
    
    // Add event listeners
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.dobInput.addEventListener('input', clearError);
    
    console.log('Next Birthday Countdown app initialized');
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const dob = elements.dobInput.value.trim();
    
    // Client-side validation
    if (!validateInput(dob)) {
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Make API call
        const result = await callBirthdayAPI(dob);
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        // Handle errors
        displayError(error.message);
    } finally {
        // Hide loading state
        hideLoading();
    }
}

// Client-side input validation
function validateInput(dob) {
    clearError();
    
    // Check if DOB is provided (trim whitespace)
    if (!dob || !dob.trim()) {
        displayError('Please enter your date of birth.');
        return false;
    }
    
    // Check date format (basic validation - browser handles most of this)
    const dobDate = new Date(dob);
    const today = new Date();
    
    // Check if date is valid
    if (isNaN(dobDate.getTime())) {
        displayError('Please enter a valid date.');
        return false;
    }
    
    // Check if date is not in the future
    if (dobDate > today) {
        displayError('Date of birth cannot be in the future.');
        return false;
    }
    
    // Check if date is not too far in the past (reasonable validation)
    const maxAge = 150;
    const minDate = new Date();
    minDate.setFullYear(minDate.getFullYear() - maxAge);
    
    if (dobDate < minDate) {
        displayError('Please enter a more recent date of birth.');
        return false;
    }
    
    return true;
}

// Call the birthday API
async function callBirthdayAPI(dob) {
    const url = `${CONFIG.API_BASE_URL}?dob=${encodeURIComponent(dob)}`;
    
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        // Handle API error responses
        if (!response.ok) {
            if (data.error) {
                throw new Error(data.error);
            } else {
                throw new Error(`API request failed with status ${response.status}`);
            }
        }
        
        // Validate response structure
        if (!isValidResponse(data)) {
            throw new Error('Invalid response format from API');
        }
        
        return data;
        
    } catch (error) {
        // Handle network errors and other exceptions
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Unable to connect to the birthday service. Please check your internet connection and try again.');
        } else if (error.message.includes('CORS')) {
            throw new Error('Unable to connect to the birthday service due to CORS policy. Please check the server configuration.');
        } else {
            throw error;
        }
    }
}

// Validate API response structure
function isValidResponse(data) {
    const requiredFields = [
        'inputDob',
        'ageYears',
        'nextBirthdayDate',
        'nextBirthdayDayOfWeek',
        'daysUntilNextBirthday',
        'message'
    ];
    
    return requiredFields.every(field => data.hasOwnProperty(field));
}

// Display successful results
function displayResults(data) {
    hideError();
    
    // Add success state to form
    elements.form.classList.add('success');
    
    // Populate result fields
    elements.ageYears.textContent = `${data.ageYears} years old`;
    elements.nextBirthdayDate.textContent = formatDate(data.nextBirthdayDate);
    elements.nextBirthdayDayOfWeek.textContent = data.nextBirthdayDayOfWeek;
    elements.daysUntilNextBirthday.textContent = `${data.daysUntilNextBirthday} days`;
    elements.message.textContent = data.message;
    
    // Show results
    elements.results.classList.remove('hidden');
    elements.results.classList.add('show');
    
    // Scroll to results
    elements.results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Format date for display
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        return dateString; // Fallback to original string
    }
}

// Display error message
function displayError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.remove('hidden');
    elements.errorMessage.classList.add('show');
    
    // Add error state to input
    elements.dobInput.classList.add('error');
    
    // Remove success state from form
    elements.form.classList.remove('success');
    
    // Hide results if showing
    hideResults();
    
    // Scroll to error
    elements.errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Clear error message
function clearError() {
    elements.errorMessage.classList.add('hidden');
    elements.errorMessage.classList.remove('show');
    
    // Remove error state from input
    elements.dobInput.classList.remove('error');
}

// Hide error message
function hideError() {
    clearError();
}

// Hide results
function hideResults() {
    elements.results.classList.add('hidden');
    elements.results.classList.remove('show');
    
    // Remove success state from form
    elements.form.classList.remove('success');
}

// Show loading state
function showLoading() {
    elements.loading.classList.remove('hidden');
    elements.loading.classList.add('show');
    elements.calculateBtn.disabled = true;
    elements.calculateBtn.textContent = 'Calculating...';
    
    // Hide previous results and errors
    hideResults();
    hideError();
}

// Hide loading state
function hideLoading() {
    elements.loading.classList.add('hidden');
    elements.loading.classList.remove('show');
    elements.calculateBtn.disabled = false;
    elements.calculateBtn.textContent = 'Calculate Next Birthday';
}

// Configuration helper for changing API URL
function setAPIBaseURL(url) {
    CONFIG.API_BASE_URL = url;
    console.log(`API base URL updated to: ${url}`);
}

// Export configuration function for external use
window.NextBirthdayCountdown = {
    setAPIBaseURL: setAPIBaseURL,
    config: CONFIG
};

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}