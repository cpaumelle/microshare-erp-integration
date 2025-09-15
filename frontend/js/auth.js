// Authentication management for Microshare ERP Integration
// Completely rewritten to fix initialization issues

class AuthManager {
    constructor() {
        this.sessionToken = localStorage.getItem(CONFIG.STORAGE.SESSION_TOKEN);
        this.userInfo = this.getUserInfo();
        this.apiBase = localStorage.getItem(CONFIG.STORAGE.API_BASE);
    }

    isAuthenticated() {
        return !!this.sessionToken && !!this.userInfo;
    }

    getUserInfo() {
        const userInfo = localStorage.getItem(CONFIG.STORAGE.USER_INFO);
        return userInfo ? JSON.parse(userInfo) : null;
    }

    async initializeAuth() {
        const isLoginPage = window.location.pathname.includes('index.html') || window.location.pathname === '/';

        if (this.isAuthenticated()) {
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

    clearAuthData() {
        localStorage.removeItem(CONFIG.STORAGE.SESSION_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE.USER_INFO);
        localStorage.removeItem(CONFIG.STORAGE.API_BASE);
        localStorage.removeItem(CONFIG.STORAGE.ENVIRONMENT);

        this.sessionToken = null;
        this.userInfo = null;
        this.apiBase = null;
    }

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

        if (response.status === 401) {
            this.clearAuthData();
            UI.showNotification('Session expired. Please log in again.', 'warning');
            this.redirectToLogin();
            throw new Error('Authentication expired');
        }

        return response;
    }

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

    async logout() {
        try {
            if (this.sessionToken) {
                await this.makeAuthenticatedRequest(
                    ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.AUTH.LOGOUT),
                    { method: 'POST' }
                );
            }
        } catch (error) {
            console.warn('Logout API call failed:', error);
        }

        this.clearAuthData();
        UI.showNotification('Logged out successfully', 'info');
        this.redirectToLogin();
    }

    redirectToLogin() {
        if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
            window.location.href = '/index.html';
        }
    }

    redirectToDashboard() {
        if (window.location.pathname !== '/dashboard.html') {
            window.location.href = '/dashboard.html';
        }
    }

    setupAuthUI() {
        const userInfoElement = document.getElementById('user-info');
        const logoutButton = document.getElementById('logout-btn');

        if (this.isAuthenticated() && userInfoElement && logoutButton) {
            userInfoElement.textContent = `${this.userInfo.username} (${this.userInfo.environment})`;
            userInfoElement.classList.remove('d-none');
            logoutButton.classList.remove('d-none');
            logoutButton.addEventListener('click', () => this.logout());
        }
    }

    setupLoginForm() {
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
                setTimeout(() => {
                    this.redirectToDashboard();
                }, 1000);
            } catch (error) {
                console.error('Login error:', error);
            }
        });

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

    startSessionRefresh() {
        setInterval(async () => {
            if (this.isAuthenticated()) {
                const isValid = await this.validateSession();
                if (!isValid) {
                    UI.showNotification('Session expired. Please log in again.', 'warning');
                    this.logout();
                }
            }
        }, CONFIG.UI.REFRESH_INTERVAL * 2);
    }
}

// Create the instance and assign to window
window.AuthManager = new AuthManager();

// Debug verification
console.log('🔧 AuthManager created:', {
    type: typeof window.AuthManager,
    constructor: window.AuthManager.constructor.name,
    hasInitializeAuth: typeof window.AuthManager.initializeAuth,
    methods: Object.getOwnPropertyNames(Object.getPrototypeOf(window.AuthManager))
});