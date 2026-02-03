// Enhanced logging configuration
const LOGGING = {
    enabled: true,
    level: 'DEBUG', // DEBUG, INFO, WARN, ERROR
    prefix: '🎂 Birthday App'
};

// Enhanced logging functions
function logDebug(...args) {
    if (LOGGING.enabled && ['DEBUG'].includes(LOGGING.level)) {
        console.log(`${LOGGING.prefix} [DEBUG]`, ...args);
    }
}

function logInfo(...args) {
    if (LOGGING.enabled && ['DEBUG', 'INFO'].includes(LOGGING.level)) {
        console.log(`${LOGGING.prefix} [INFO]`, ...args);
    }
}

function logWarn(...args) {
    if (LOGGING.enabled && ['DEBUG', 'INFO', 'WARN'].includes(LOGGING.level)) {
        console.warn(`${LOGGING.prefix} [WARN]`, ...args);
    }
}

function logError(...args) {
    if (LOGGING.enabled) {
        console.error(`${LOGGING.prefix} [ERROR]`, ...args);
    }
}

// Configuration
const CONFIG = {
    // Try multiple API endpoints in order of preference
    API_ENDPOINTS: [
        // Azure Static Web Apps integrated API (preferred)
        '/api/nextbirthday',
        // Fallback to external Azure Functions if integrated API fails
        'https://funchttptrigger1-fvbnfye7bac5bgd5.eastus-01.azurewebsites.net/api/nextbirthday'
    ],
    // Current API URL (will be set dynamically)
    API_BASE_URL: window.location.hostname.includes('localhost') 
        ? 'http://localhost:8000/api/nextbirthday'  // Local development
        : '/api/nextbirthday'  // Use integrated API for Azure Static Web Apps
};

// Deployment info for debugging
logInfo('Birthday Countdown App v2.4 - CI/CD Test & Application Insights Ready:', new Date().toISOString());
logInfo('Environment:', window.location.hostname.includes('localhost') ? 'LOCAL' : 'AZURE');
logInfo('Hostname:', window.location.hostname);
logInfo('Full URL:', window.location.href);
logInfo('API Configuration:', CONFIG);
console.log('🌍 Environment:', window.location.hostname.includes('localhost') ? 'LOCAL' : 'AZURE');
console.log('🔗 API URL:', CONFIG.API_BASE_URL);

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
    logInfo('=== Initializing Birthday Countdown App ===');
    
    // Set max date to today to prevent future dates
    const today = new Date().toISOString().split('T')[0];
    elements.dobInput.setAttribute('max', today);
    logDebug('Set max date to:', today);
    
    // Add event listeners
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.dobInput.addEventListener('input', clearError);
    
    // Ensure date input works properly
    elements.dobInput.addEventListener('focus', function() {
        logDebug('Date input focused');
        // Force the date picker to show
        this.showPicker && this.showPicker();
    });
    
    logInfo('Birthday Countdown app initialized successfully');
    logInfo('DOM elements found:', {
        form: !!elements.form,
        dobInput: !!elements.dobInput,
        errorMessage: !!elements.errorMessage,
        results: !!elements.results,
        loading: !!elements.loading
    });
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    logInfo('=== Form submission started ===');
    const dob = elements.dobInput.value.trim();
    logInfo('Form DOB value:', dob);
    
    // Client-side validation
    if (!validateInput(dob)) {
        logWarn('Client-side validation failed');
        return;
    }
    
    logInfo('Client-side validation passed');
    
    // Show loading state
    showLoading();
    
    try {
        // Use the formatted date for API call
        const formattedDate = elements.dobInput.dataset.formattedDate || dob;
        logInfo('Using formatted date for API:', formattedDate);
        
        // Make API call
        const result = await callBirthdayAPI(formattedDate);
        
        // Display results
        logInfo('Displaying results');
        displayResults(result);
        
    } catch (error) {
        // Handle errors
        logError('Form submission error:', error);
        displayError(error.message);
    } finally {
        // Hide loading state
        hideLoading();
        logInfo('=== Form submission completed ===');
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
    
    // Convert DD/MM/YYYY to YYYY-MM-DD format for API
    let formattedDate = dob;
    
    // Handle different date formats
    if (dob.includes('/')) {
        const parts = dob.split('/');
        if (parts.length === 3) {
            // Assume DD/MM/YYYY format (European style)
            const day = parts[0].padStart(2, '0');
            const month = parts[1].padStart(2, '0');
            const year = parts[2];
            
            // Validate year length
            if (year.length === 2) {
                // Convert 2-digit year to 4-digit (assume 1900s for years > 50, 2000s for years <= 50)
                const currentYear = new Date().getFullYear();
                const century = parseInt(year) > 50 ? 1900 : 2000;
                formattedDate = `${century + parseInt(year)}-${month}-${day}`;
            } else if (year.length === 4) {
                formattedDate = `${year}-${month}-${day}`;
            } else {
                displayError('Please enter a valid year (YYYY or YY format).');
                return false;
            }
        } else {
            displayError('Please enter date in DD/MM/YYYY format.');
            return false;
        }
    } else if (dob.includes('-')) {
        // Already in YYYY-MM-DD format, keep as is
        formattedDate = dob;
    } else {
        displayError('Please enter date in DD/MM/YYYY format or use the date picker.');
        return false;
    }
    
    // Validate the formatted date
    const dobDate = new Date(formattedDate);
    const today = new Date();
    
    // Check if date is valid
    if (isNaN(dobDate.getTime())) {
        displayError('Please enter a valid date. Use DD/MM/YYYY format (e.g., 12/06/2000).');
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
    
    // Store the formatted date for API call
    elements.dobInput.dataset.formattedDate = formattedDate;
    
    return true;
}

// Call the birthday API with fallback support
async function callBirthdayAPI(dob) {
    logInfo('=== Starting API call ===');
    logInfo('DOB parameter:', dob);
    logInfo('User Agent:', navigator.userAgent);
    logInfo('Current timestamp:', new Date().toISOString());
    
    let lastError = null;
    
    // For localhost, use the configured URL directly
    if (window.location.hostname.includes('localhost')) {
        logInfo('Using localhost configuration');
        return await makeAPIRequest(CONFIG.API_BASE_URL, dob);
    }
    
    // For production, try multiple endpoints
    const endpoints = [
        '/api/nextbirthday',  // Integrated API (preferred)
        'https://funchttptrigger1-fvbnfye7bac5bgd5.eastus-01.azurewebsites.net/api/nextbirthday'  // External Functions
    ];
    
    logInfo('Production environment detected, trying multiple endpoints:', endpoints);
    
    for (let i = 0; i < endpoints.length; i++) {
        const endpoint = endpoints[i];
        try {
            logInfo(`🔄 Attempt ${i + 1}/${endpoints.length}: Trying endpoint: ${endpoint}`);
            const startTime = performance.now();
            
            const result = await makeAPIRequest(endpoint, dob);
            
            const endTime = performance.now();
            const duration = Math.round(endTime - startTime);
            
            logInfo(`✅ SUCCESS with endpoint: ${endpoint} (${duration}ms)`);
            logInfo('API Response:', result);
            return result;
            
        } catch (error) {
            const endTime = performance.now();
            logError(`❌ FAILED with endpoint ${endpoint}:`, {
                error: error.message,
                stack: error.stack,
                endpoint: endpoint,
                attempt: i + 1
            });
            lastError = error;
            continue;
        }
    }
    
    // If all endpoints failed, throw the last error
    logError('🚨 ALL ENDPOINTS FAILED');
    logError('Last error:', lastError);
    throw lastError || new Error('All API endpoints failed');
}

// Make API request to a specific endpoint
async function makeAPIRequest(baseUrl, dob) {
    const url = `${baseUrl}?dob=${encodeURIComponent(dob)}`;
    logDebug('Making request to:', url);
    
    const requestOptions = {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    };
    
    logDebug('Request options:', requestOptions);
    
    try {
        logDebug('Initiating fetch request...');
        const response = await fetch(url, requestOptions);
        
        logDebug('Response received:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            url: response.url
        });
        
        let data;
        try {
            data = await response.json();
            logDebug('Response data parsed:', data);
        } catch (parseError) {
            logError('Failed to parse JSON response:', parseError);
            const textResponse = await response.text();
            logError('Raw response text:', textResponse);
            throw new Error(`Invalid JSON response: ${parseError.message}`);
        }
        
        // Handle API error responses
        if (!response.ok) {
            logWarn('API returned error status:', response.status);
            if (data.error) {
                throw new Error(data.error);
            } else {
                throw new Error(`API request failed with status ${response.status}: ${response.statusText}`);
            }
        }
        
        // Validate response structure
        if (!isValidResponse(data)) {
            logError('Invalid response structure:', data);
            throw new Error('Invalid response format from API');
        }
        
        logInfo('API request successful');
        return data;
        
    } catch (error) {
        logError('API request failed:', {
            error: error.message,
            stack: error.stack,
            url: url,
            type: error.name
        });
        
        // Handle network errors and other exceptions
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Network error: Unable to connect to the birthday service. Please check your internet connection and try again.');
        } else if (error.message.includes('CORS')) {
            throw new Error('CORS error: Unable to connect to the birthday service due to cross-origin policy. Please check the server configuration.');
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