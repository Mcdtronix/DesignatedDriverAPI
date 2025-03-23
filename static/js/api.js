// API Base URL
const API_BASE_URL = '/api/';

// Function to make API calls with authorization
async function apiCall(url, method = 'GET', data = null, requiresAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (requiresAuth) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/login/'; // Redirect if no token
            return;
        }
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers,
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(API_BASE_URL + url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

// Example API call functions (You'll add more)
async function registerUser(userData) {
    return apiCall('users/', 'POST', userData, false);
}

async function loginUser(credentials) {
    const response = await fetch('/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

async function getUserProfile() {
    return apiCall('users/me/');
}