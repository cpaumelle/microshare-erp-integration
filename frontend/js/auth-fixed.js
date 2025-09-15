// Authentication management for Microshare ERP Integration

class AuthManager {
    constructor() {
        this.sessionToken = localStorage.getItem(CONFIG.STORAGE.SESSION_TOKEN);
        this.userInfo = this.getUserInfo();
        this.apiBase = localStorage.getItem(CONFIG.STORAGE.API_BASE);
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.sessionToken && !!this.userInfo;
    }

    // Get stored user information
    getUserInfo() {
        const userInfo = localStorage.getItem(CONFIG.STORAGE.USER_INFO);
        return userInfo ? JSON.parse(userInfo) : null;
    }

    // Initialize authentication state
    async initializeAuth() {
        // Check if on login page
        const isLoginPage = window.location.pathname.includes('index.html') ||
                           window.location.pathname === '/';

        if (this.isAuthenticated()) {
            // Validate session
            const isValid = await this.validateSession();

            if (isValid) {
                if (isLoginPage) {
                    this.redirectToDashboard();
                }
                return true;
            } else {
                this.clearAuthData();
                if (!isLoginPage) {
                    this.redirectToLogin();
                }
                return false;
            }
        } else {
            if (!isLoginPage) {
                this.redirectToLogin();
            }
            return false;
        }
    }

    // Validate current session
    async validateSession() {
        if (!this.sessionToken) {
            return false;
        }

        try {
            const response = await this.makeAuthenticatedRequest(
                ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.AUTH.VALIDATE)
            );

            if (response.ok) {
                const result = await response.json();
                return result.valid;
            }
            return false;
        } catch (error) {
            console.warn('Session validation failed:', error);
            return false;
        }
    }

    // Store authentication data
    storeAuthData(authResult) {
        localStorage.setItem(CONFIG.STORAGE.SESSION_TOKEN, authResult.session_token);
        localStorage.setItem(CONFIG.STORAGE.USER_INFO, JSON.stringify(authResult.user_info));
        localStorage.setItem(CONFIG.STORAGE.API_BASE, authResult.api_base);
        localStorage.setItem(CONFIG.STORAGE.ENVIRONMENT, authResult.user_info.environment);
        localStorage.setItem(CONFIG.STORAGE.LAST_LOGIN, new Date().toISOString());

        this.sessionToken = authResult.session_token;
        this.userInfo = authResult.user_info;
        this.apiBase = authResult.api_base;
    }

    // Clear authentication data
    clearAuthData() {
        localStorage.removeItem(CONFIG.STORAGE.SESSION_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE.USER_INFO);
        localStorage.removeItem(CONFIG.STORAGE.API_BASE);
        localStorage.removeItem(CONFIG.STORAGE.ENVIRONMENT);

        this.sessionToken = null;
        this.userInfo = null;
        this.apiBase = null;
    }

    // Make authenticated API request
    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.sessionToken) {
            throw new Error('No authentication token available');
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.sessionToken}`,
            ...options.headers
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle authentication errors
        if (response.status === 401) {
            this.clearAuthData();
            UI.showNotification('Session expired. Please log in again.', 'warning');
            this.redirectToLogin();
            throw new Error('Authentication expired');
        }

        return response;
    }

    // Login with username and password
    async login(username, password, environment = 'dev') {
        try {
            UI.showLoadingSpinner(true);
            UI.updateStatus('Authenticating with Microshare...', 'info');

            const response = await fetch(ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.AUTH.LOGIN), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password,
                    environment
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.storeAuthData(result);

                UI.showNotification(`Welcome back, ${username}!`, 'success');
                UI.updateStatus('Authentication successful', 'success');

                return result;
            } else {
                throw new Error(result.detail || 'Authentication failed');
            }
        } catch (error) {
            UI.showNotification(`Login failed: ${error.message}`, 'danger');
            UI.updateStatus('Authentication failed', 'danger');
            throw error;
        } finally {
            UI.showLoadingSpinner(false);
        }
    }

    // Logout user
    async logout() {
        try {
            // Attempt to call logout endpoint
            if (this.sessionToken) {
                await this.makeAuthenticatedRequest(
                    ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.AUTH.LOGOUT),
                    { method: 'POST' }
                );
            }
        } catch (error) {
            console.warn('Logout API call failed:', error);
            // Continue with local logout even if API call fails
        }

        this.clearAuthData();
        UI.showNotification('Logged out successfully', 'info');
        this.redirectToLogin();
    }

    // Redirect to login page
    redirectToLogin() {
        if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
            window.location.href = '/index.html';
        }
    }

    // Redirect to dashboard
    redirectToDashboard() {
        if (window.location.pathname !== '/dashboard.html') {
            window.location.href = '/dashboard.html';
        }
    }

    // Set up authentication UI
    setupAuthUI() {
        // Update user info in navbar
        const userInfoElement = document.getElementById('user-info');
        const logoutButton = document.getElementById('logout-btn');

        if (this.isAuthenticated() && userInfoElement && logoutButton) {
            userInfoElement.textContent = `${this.userInfo.username} (${this.userInfo.environment})`;
            userInfoElement.classList.remove('d-none');
            logoutButton.classList.remove('d-none');

            // Add logout handler
            logoutButton.addEventListener('click', () => this.logout());
        }
    }

    // Handle login form submission
    setupLoginForm() {
        // Wait for login form to be loaded by component system
        const checkForm = () => {
            const loginForm = document.getElementById('loginForm');
            if (!loginForm) {
                setTimeout(checkForm, 100);
                return;
            }
            this.attachFormHandlers(loginForm);
        };
        checkForm();
    }

    // Attach form event handlers
    attachFormHandlers(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = UI.getFormData('loginForm');

            if (!formData.username || !formData.password) {
                UI.showNotification('Please enter both username and password', 'warning');
                return;
            }

            try {
                await this.login(formData.username, formData.password, formData.environment);

                // Redirect to dashboard after successful login
                setTimeout(() => {
                    this.redirectToDashboard();
                }, 1000);

            } catch (error) {
                console.error('Login error:', error);
                // Error already handled in login method
            }
        });

        // Pre-fill demo credentials in development
        if (window.location.hostname === 'localhost' ||
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname === '10.35.1.112') {
            UI.populateForm('loginForm', {
                username: CONFIG.DEMO.USERNAME,
                password: CONFIG.DEMO.PASSWORD,
                environment: CONFIG.DEMO.ENVIRONMENT
            });
        }
    }

    // Auto-refresh session periodically
    startSessionRefresh() {
        setInterval(async () => {
            if (this.isAuthenticated()) {
                const isValid = await this.validateSession();
                if (!isValid) {
                    UI.showNotification('Session expired. Please log in again.', 'warning');
                    this.logout();
                }
            }
        }, CONFIG.UI.REFRESH_INTERVAL * 2); // Check every minute
    }
}

// Create global auth manager instance immediately
window.AuthManager = new AuthManager();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}