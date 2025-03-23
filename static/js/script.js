// Example functions to handle UI interactions
document.addEventListener('DOMContentLoaded', () => {
    // Example: Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        // User is logged in
    } else {
        // User is logged out
    }
});

// Example function to handle form submission
async function handleLoginForm(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const data = await loginUser({ username, password });
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        window.location.href = '/profile/';
    } catch (error) {
        console.error('Login failed:', error);
        // Display error message to the user
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = 'Login failed. Please check your credentials.';
        } else {
            //Create the error div
            const errorDiv = document.createElement('div');
            errorDiv.id = 'login-error';
            errorDiv.textContent = 'Login failed. Please check your credentials.';
            document.getElementById('login-form').prepend(errorDiv);
        }
    }
}

// ... (existing code)

// Example function to handle logout
function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login/';
}

// Attach logout to a button or link
document.addEventListener('DOMContentLoaded', () => {
    const logoutLink = document.querySelector('a[href="/logout/"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
});