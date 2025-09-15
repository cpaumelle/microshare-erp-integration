// Main application initialization and coordination
// Completely rewritten to fix initialization issues

class Application {
    constructor() {
        this.initialized = false;
        this.currentPage = this.getCurrentPage();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('dashboard') || path.includes('dashboard.html')) {
            return 'dashboard';
        } else if (path.includes('index') || path === '/') {
            return 'login';
        }
        return 'unknown';
    }

    async initialize() {
        if (this.initialized) return;

        try {
            console.log('🚀 Initializing Microshare ERP Integration Frontend v3.0');

            // Verify AuthManager is properly initialized
            if (!window.AuthManager || typeof window.AuthManager.initializeAuth !== 'function') {
                throw new Error('AuthManager not properly initialized');
            }

            // Initialize authentication
            const isAuthenticated = await window.AuthManager.initializeAuth();

            // Set up page-specific functionality
            if (this.currentPage === 'login') {
                this.initializeLoginPage();
            } else if (this.currentPage === 'dashboard' && isAuthenticated) {
                await this.initializeDashboard();
            }

            // Set up global error handling
            this.setupErrorHandling();

            // Set up keyboard shortcuts
            this.setupKeyboardShortcuts();

            this.initialized = true;
            console.log('✅ Application initialized successfully');
            console.log(`%c🔧 FRONTEND VERSION INFO`, 'color: #28a745; font-weight: bold; font-size: 14px;');
            console.log(`%cVersion: ${CONFIG.BUILD.VERSION}`, 'color: #007bff; font-weight: bold;');
            console.log(`%cBuild Time: ${CONFIG.BUILD.BUILD_TIME}`, 'color: #007bff; font-weight: bold;');
            console.log(`%cBuild Number: ${CONFIG.BUILD.BUILD_NUMBER}`, 'color: #007bff; font-weight: bold;');

            // Update build info in header
            this.updateBuildInfo();

        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.showError(`Application failed to initialize: ${error.message}`);
        }
    }

    initializeLoginPage() {
        console.log('🔐 Setting up login page');

        // Set up authentication form
        window.AuthManager.setupLoginForm();

        // Check if already authenticated
        if (window.AuthManager.isAuthenticated()) {
            this.showInfo('Already logged in, redirecting...');
            setTimeout(() => {
                window.AuthManager.redirectToDashboard();
            }, 1000);
        }

        // Add demo info
        this.showDemoInfo();
    }

    async initializeDashboard() {
        console.log('📊 Setting up dashboard');

        // Set up authentication UI
        window.AuthManager.setupAuthUI();

        // Verify DeviceManager is available
        if (!window.DeviceManager || typeof window.DeviceManager.initialize !== 'function') {
            throw new Error('DeviceManager not properly initialized');
        }

        // Initialize device manager with cache warming
        this.showInfo('Warming cache for optimal performance...');
        await window.DeviceManager.initialize();

        // Start session refresh
        window.AuthManager.startSessionRefresh();

        // Set up additional dashboard features
        this.setupDashboardFeatures();

        this.showSuccess(`Dashboard loaded successfully - v${CONFIG.BUILD.VERSION}`);

        // Add version info to page
        this.addVersionInfo();
    }

    setupDashboardFeatures() {
        // Add keyboard shortcuts info
        this.addKeyboardShortcutsInfo();

        // Set up refresh timer display
        this.setupRefreshTimer();

        // Add performance monitoring
        this.setupPerformanceMonitoring();
    }

    showDemoInfo() {
        if (window.location.hostname === 'localhost' ||
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname === '10.35.1.112') {
            setTimeout(() => {
                this.showInfo('Demo mode: Credentials are pre-filled for testing', 10000);
            }, 2000);
        }
    }

    setupErrorHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('An unexpected error occurred');
        });

        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An error occurred while processing your request');
        });

        window.addEventListener('offline', () => {
            this.showWarning('You are offline. Some features may not work.');
        });

        window.addEventListener('online', () => {
            this.showSuccess('Connection restored');
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + R: Refresh (prevent default and use our refresh)
            if ((e.ctrlKey || e.metaKey) && e.key === 'r' && this.currentPage === 'dashboard') {
                e.preventDefault();
                if (window.DeviceManager && window.DeviceManager.loadDevices) {
                    window.DeviceManager.loadDevices();
                }
            }

            // Ctrl/Cmd + N: Add new device (dashboard only)
            if ((e.ctrlKey || e.metaKey) && e.key === 'n' && this.currentPage === 'dashboard') {
                e.preventDefault();
                if (window.DeviceManager && window.DeviceManager.showAddDeviceModal) {
                    window.DeviceManager.showAddDeviceModal();
                }
            }

            // Ctrl/Cmd + D: Discover devices (dashboard only)
            if ((e.ctrlKey || e.metaKey) && e.key === 'd' && this.currentPage === 'dashboard') {
                e.preventDefault();
                if (window.DeviceManager && window.DeviceManager.discoverDevices) {
                    window.DeviceManager.discoverDevices();
                }
            }

            // Ctrl/Cmd + L: Logout (dashboard only)
            if ((e.ctrlKey || e.metaKey) && e.key === 'l' && this.currentPage === 'dashboard') {
                e.preventDefault();
                if (window.AuthManager && window.AuthManager.logout) {
                    window.AuthManager.logout();
                }
            }
        });
    }

    updateBuildInfo() {
        // Update build info in header
        const buildInfoElement = document.getElementById('build-info');
        if (buildInfoElement) {
            const buildTime = new Date(CONFIG.BUILD.BUILD_TIME).toLocaleString();
            buildInfoElement.textContent = `Build: v${CONFIG.BUILD.VERSION} | ${buildTime}`;
        }
    }

    addVersionInfo() {
        const versionInfo = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6 class="mb-0">ℹ️ System Information</h6>
                </div>
                <div class="card-body">
                    <small class="text-muted">
                        <strong>Version:</strong> ${CONFIG.BUILD.VERSION} &nbsp;|&nbsp;
                        <strong>Build:</strong> ${CONFIG.BUILD.BUILD_TIME} &nbsp;|&nbsp;
                        <strong>Cache Status:</strong> <span id="cache-status-indicator">Checking...</span>
                    </small>
                </div>
            </div>
        `;

        const container = document.querySelector('.container');
        if (container && this.currentPage === 'dashboard') {
            container.insertAdjacentHTML('beforeend', versionInfo);
        }
    }

    addKeyboardShortcutsInfo() {
        const shortcutsInfo = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6 class="mb-0">⌨️ Keyboard Shortcuts</h6>
                </div>
                <div class="card-body">
                    <small class="text-muted">
                        <strong>Ctrl+R:</strong> Refresh devices &nbsp;|&nbsp;
                        <strong>Ctrl+N:</strong> Add device &nbsp;|&nbsp;
                        <strong>Ctrl+D:</strong> Discover devices &nbsp;|&nbsp;
                        <strong>Ctrl+L:</strong> Logout
                    </small>
                </div>
            </div>
        `;

        const container = document.querySelector('.container');
        if (container && this.currentPage === 'dashboard') {
            container.insertAdjacentHTML('beforeend', shortcutsInfo);
        }
    }

    setupRefreshTimer() {
        let refreshCountdown = CONFIG.UI.REFRESH_INTERVAL / 1000;

        const updateCountdown = () => {
            const timerElement = document.getElementById('refresh-timer');
            if (timerElement) {
                timerElement.textContent = `Next refresh: ${refreshCountdown}s`;
            }

            refreshCountdown--;
            if (refreshCountdown < 0) {
                refreshCountdown = CONFIG.UI.REFRESH_INTERVAL / 1000;
            }
        };

        // Add timer element to status bar if it doesn't exist
        const statusMessage = document.getElementById('status-message');
        if (statusMessage && !document.getElementById('refresh-timer')) {
            statusMessage.insertAdjacentHTML('afterend',
                '<small id="refresh-timer" class="text-muted ms-3"></small>'
            );
        }

        setInterval(updateCountdown, 1000);
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            console.log(`📈 Page loaded in ${loadTime.toFixed(2)}ms`);

            if (loadTime > 3000) {
                this.showWarning('Page loaded slowly. Check your connection.');
            }
        });

        // Monitor memory usage (if supported)
        if (performance.memory) {
            setInterval(() => {
                const memory = performance.memory;
                const usedMB = Math.round(memory.usedJSHeapSize / 1048576);

                if (usedMB > 100) {
                    console.warn(`⚠️ High memory usage: ${usedMB}MB`);
                }
            }, 60000); // Check every minute
        }
    }

    setupVisibilityHandling() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden, pause auto-refresh
                if (window.DeviceManager && window.DeviceManager.stopAutoRefresh) {
                    window.DeviceManager.stopAutoRefresh();
                }
            } else {
                // Page is visible, resume auto-refresh and refresh data
                if (window.AuthManager && window.AuthManager.isAuthenticated() && this.currentPage === 'dashboard') {
                    if (window.DeviceManager) {
                        if (window.DeviceManager.startAutoRefresh) {
                            window.DeviceManager.startAutoRefresh();
                        }
                        if (window.DeviceManager.loadDevices) {
                            window.DeviceManager.loadDevices();
                        }
                    }
                }
            }
        });
    }

    // Notification helpers
    showSuccess(message, duration = 5000) {
        if (window.UI && window.UI.showNotification) {
            window.UI.showNotification(message, 'success', duration);
        } else {
            console.log('✅', message);
        }
    }

    showError(message, duration = 10000) {
        if (window.UI && window.UI.showNotification) {
            window.UI.showNotification(message, 'danger', duration);
        } else {
            console.error('❌', message);
        }
    }

    showWarning(message, duration = 7000) {
        if (window.UI && window.UI.showNotification) {
            window.UI.showNotification(message, 'warning', duration);
        } else {
            console.warn('⚠️', message);
        }
    }

    showInfo(message, duration = 5000) {
        if (window.UI && window.UI.showNotification) {
            window.UI.showNotification(message, 'info', duration);
        } else {
            console.info('ℹ️', message);
        }
    }

    // Get application status for debugging
    getStatus() {
        return {
            initialized: this.initialized,
            currentPage: this.currentPage,
            authenticated: window.AuthManager ? window.AuthManager.isAuthenticated() : false,
            userInfo: window.AuthManager ? window.AuthManager.getUserInfo() : null,
            deviceCount: window.DeviceManager ? window.DeviceManager.devices.length : 0,
            stats: window.DeviceManager ? window.DeviceManager.stats : {}
        };
    }

    // Reset application state (for debugging)
    reset() {
        if (window.AuthManager && window.AuthManager.clearAuthData) {
            window.AuthManager.clearAuthData();
        }
        if (window.DeviceManager && window.DeviceManager.stopAutoRefresh) {
            window.DeviceManager.stopAutoRefresh();
        }
        if (window.UI && window.UI.clearContainer) {
            window.UI.clearContainer('devices-container');
        }
        this.initialized = false;
        window.location.reload();
    }
}

// Create global application instance
window.App = new Application();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, initializing app...');
    window.App.initialize();
});

// Export for debugging and testing
window.AppStatus = () => window.App.getStatus();
window.AppReset = () => window.App.reset();

console.log('🔧 Microshare ERP Integration Frontend modules loaded');
console.log('📝 Available global objects: CONFIG, UI, AuthManager, DeviceManager, App');
console.log('🐛 Debug commands: AppStatus(), AppReset()');

// Debug verification
console.log('🔧 App created:', {
    type: typeof window.App,
    constructor: window.App.constructor.name,
    currentPage: window.App.currentPage,
    initialized: window.App.initialized
});