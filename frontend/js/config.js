// Configuration for Microshare ERP Integration Frontend
// Build: 2025-09-15-14:05:00 - CACHE BUSTING ACTIVE

// IMMEDIATE CONSOLE OUTPUT
console.log(`%c🚀 MICROSHARE ERP INTEGRATION FRONTEND`, 'background: #28a745; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; font-size: 16px;');
console.log(`%c📦 Version: 3.0.1 | Build: 2025-09-15T14:05:00Z`, 'color: #007bff; font-weight: bold; font-size: 14px;');
console.log(`%c⚡ Cache busting enabled - You're running the latest code!`, 'color: #28a745; font-weight: bold;');

const CONFIG = {
    // Build Information
    BUILD: {
        VERSION: '3.0.1',
        BUILD_TIME: '2025-09-15T14:05:00Z',
        BUILD_NUMBER: Date.now() // Dynamic build number
    },
    // API Configuration
    API: {
        BASE_URL: window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'http://10.35.1.112:8000',
        ENDPOINTS: {
            AUTH: {
                LOGIN: '/api/v1/auth/login',
                LOGOUT: '/api/v1/auth/logout',
                STATUS: '/api/v1/auth/status',
                VALIDATE: '/api/v1/auth/validate-token'
            },
            DEVICES: {
                LIST: '/api/v1/devices/',
                CREATE: '/api/v1/devices/create',
                UPDATE: '/api/v1/devices/',
                DELETE: '/api/v1/devices/',
                DISCOVERY: '/api/v1/devices/test',
                CLUSTERS: '/api/v1/devices/test',
                BENCHMARK: '/api/v1/devices/performance/benchmark'
            },
            HEALTH: '/health'
        }
    },

    // Environment Settings
    ENVIRONMENTS: {
        DEV: {
            name: 'Development',
            description: 'dapi.microshare.io',
            value: 'dev'
        },
        PROD: {
            name: 'Production',
            description: 'api.microshare.io',
            value: 'prod'
        }
    },

    // Demo Credentials (for development)
    DEMO: {
        USERNAME: 'cp_erp_sample@maildrop.cc',
        PASSWORD: 'AVH7dbz!brt-rfn0tdk',
        ENVIRONMENT: 'dev'
    },

    // Device Types
    DEVICE_TYPES: {
        RODENT_SENSOR: {
            type: 'io.microshare.trap.packed',
            name: 'Rodent Sensor',
            locationFields: [
                'Customer',
                'Site',
                'Area',
                'ERP Reference',
                'Placement',
                'Configuration'
            ]
        },
        GATEWAY: {
            type: 'io.microshare.gateway.health.packed',
            name: 'Gateway',
            locationFields: [
                'Customer',
                'Site',
                'Area',
                'Gateway Location'
            ]
        }
    },

    // UI Settings
    UI: {
        REFRESH_INTERVAL: 30000, // 30 seconds
        NOTIFICATION_TIMEOUT: 5000, // 5 seconds
        LOADING_DELAY: 500, // 500ms before showing spinner
        PAGINATION_SIZE: 10
    },

    // Local Storage Keys
    STORAGE: {
        SESSION_TOKEN: 'microshare_session_token',
        USER_INFO: 'user_info',
        API_BASE: 'api_base',
        ENVIRONMENT: 'environment',
        LAST_LOGIN: 'last_login'
    },

    // Status Types
    STATUS: {
        ACTIVE: 'active',
        PENDING: 'pending',
        FAILED: 'failed',
        UNKNOWN: 'unknown'
    },

    // Placement Options
    PLACEMENT_OPTIONS: [
        'Internal',
        'External'
    ],

    // Configuration Options
    CONFIGURATION_OPTIONS: [
        'Bait/Lured',
        'Unbaited',
        'Monitoring Only'
    ]
};

// Utility functions for configuration
const ConfigUtils = {
    // Get full API URL
    getApiUrl(endpoint) {
        return CONFIG.API.BASE_URL + endpoint;
    },

    // Get device type by record type
    getDeviceType(recordType) {
        return Object.values(CONFIG.DEVICE_TYPES).find(type => type.type === recordType);
    },

    // Get status display information
    getStatusInfo(status) {
        const statusMap = {
            [CONFIG.STATUS.ACTIVE]: {
                label: 'Active',
                class: 'status-active',
                badge: 'success'
            },
            [CONFIG.STATUS.PENDING]: {
                label: 'Pending',
                class: 'status-pending',
                badge: 'warning'
            },
            [CONFIG.STATUS.FAILED]: {
                label: 'Failed',
                class: 'status-failed',
                badge: 'danger'
            }
        };
        return statusMap[status] || {
            label: 'Unknown',
            class: 'status-unknown',
            badge: 'secondary'
        };
    },

    // Format device ID for display
    formatDeviceId(deviceId) {
        if (!deviceId || deviceId === '00-00-00-00-00-00-00-00') {
            return 'Pending Assignment';
        }
        return deviceId.toUpperCase();
    },

    // Validate environment
    isValidEnvironment(env) {
        return Object.values(CONFIG.ENVIRONMENTS).some(e => e.value === env);
    }
};

// Export for use in other modules
window.CONFIG = CONFIG;
window.ConfigUtils = ConfigUtils;