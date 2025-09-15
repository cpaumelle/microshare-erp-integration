// Device management for Microshare ERP Integration

class DeviceManager {
    constructor() {
        this.devices = [];
        this.clusters = [];
        this.stats = {
            totalDevices: 0,
            activeDevices: 0,
            pendingDevices: 0,
            totalClusters: 0
        };
        this.refreshInterval = null;
    }

    // Initialize device manager
    async initialize() {
        if (!AuthManager.isAuthenticated()) {
            return;
        }

        this.setupEventHandlers();
        await this.loadDevices();
        this.startAutoRefresh();
    }

    // Set up event handlers
    setupEventHandlers() {
        // Discover devices button
        UI.addEventHandler('discover-btn', 'click', () => this.discoverDevices());

        // Add device button
        UI.addEventHandler('add-device-btn', 'click', () => this.showAddDeviceModal());

        // Refresh button
        UI.addEventHandler('refresh-btn', 'click', () => this.loadDevices());

        // Modal close handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal')) {
                this.hideModals();
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModals();
            }
        });
    }

    // Load all devices
    async loadDevices() {
        try {
            const startTime = Date.now();
            UI.setLoading('refresh-btn', true, 'Loading...');
            UI.showLoadingSpinner(true);
            UI.updateStatus('Loading devices...', 'info');

            const response = await AuthManager.makeAuthenticatedRequest(
                ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.LIST)
            );

            if (response.ok) {
                const data = await response.json();
                this.devices = data.devices || [];
                this.clusters = data.clusters || [];

                this.updateStats();
                this.renderDevices();

                const loadTime = Date.now() - startTime;
                const cacheStatus = data.performance_metrics?.cache_status || 'unknown';
                const responseTime = data.performance_metrics?.response_time_seconds || (loadTime / 1000);

                if (responseTime > 10) {
                    UI.showNotification(`Loaded ${this.devices.length} devices (cache warming took ${responseTime.toFixed(1)}s)`, 'warning');
                } else {
                    UI.showNotification(`Loaded ${this.devices.length} devices (${responseTime.toFixed(1)}s)`, 'success');
                }

                UI.updateStatus(`${this.devices.length} devices loaded - Cache: ${cacheStatus}`, 'success');
            } else {
                throw new Error('Failed to load devices');
            }
        } catch (error) {
            UI.showNotification(`Error loading devices: ${error.message}`, 'danger');
            UI.updateStatus('Failed to load devices', 'danger');
        } finally {
            UI.setLoading('refresh-btn', false);
            UI.showLoadingSpinner(false);
        }
    }

    // Discover devices from Microshare
    async discoverDevices() {
        try {
            UI.setLoading('discover-btn', true, 'Discovering...');
            UI.updateStatus('Discovering devices from Microshare...', 'info');

            const response = await AuthManager.makeAuthenticatedRequest(
                ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.DISCOVERY)
            );

            if (response.ok) {
                const data = await response.json();

                UI.showNotification(
                    `Discovery complete: ${data.devices_found || 0} devices, ${data.clusters_found || 0} clusters`,
                    'success'
                );

                // Reload devices to get updated data
                await this.loadDevices();
            } else {
                throw new Error('Device discovery failed');
            }
        } catch (error) {
            UI.showNotification(`Discovery error: ${error.message}`, 'danger');
            UI.updateStatus('Discovery failed', 'danger');
        } finally {
            UI.setLoading('discover-btn', false);
        }
    }

    // Update statistics
    updateStats() {
        this.stats = {
            totalDevices: this.devices.length,
            activeDevices: this.devices.filter(d => d.status === CONFIG.STATUS.ACTIVE).length,
            pendingDevices: this.devices.filter(d => d.status === CONFIG.STATUS.PENDING).length,
            totalClusters: this.clusters.length
        };

        UI.updateStats(this.stats);
    }

    // Render devices to UI
    renderDevices() {
        const container = document.getElementById('devices-container');
        if (!container) return;

        if (this.devices.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <h5>No devices found</h5>
                    <p>Click "Discover Devices" to scan for devices in your Microshare clusters.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.devices.map(device =>
            UI.createDeviceCard(device)
        ).join('');
    }

    // Show add device modal
    showAddDeviceModal() {
        this.loadAddDeviceForm();
        UI.showModal('addDeviceModal');
    }

    // Load add device form
    loadAddDeviceForm() {
        const container = document.getElementById('add-device-form-container');
        if (!container) return;

        const deviceType = CONFIG.DEVICE_TYPES.RODENT_SENSOR; // Default to rodent sensor

        container.innerHTML = `
            <form id="addDeviceForm">
                <div class="form-group">
                    <label class="form-label">Device Type</label>
                    <select name="deviceType" class="form-control form-select" onchange="DeviceManager.updateLocationFields(this.value)">
                        <option value="${CONFIG.DEVICE_TYPES.RODENT_SENSOR.type}">${CONFIG.DEVICE_TYPES.RODENT_SENSOR.name}</option>
                        <option value="${CONFIG.DEVICE_TYPES.GATEWAY.type}">${CONFIG.DEVICE_TYPES.GATEWAY.name}</option>
                    </select>
                </div>

                <div id="location-fields">
                    ${this.renderLocationFields(deviceType)}
                </div>

                <div class="form-group">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-control form-select">
                        <option value="${CONFIG.STATUS.PENDING}">Pending</option>
                        <option value="${CONFIG.STATUS.ACTIVE}">Active</option>
                    </select>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="UI.hideModal('addDeviceModal')">Cancel</button>
                    <button type="submit" class="btn btn-success">Add Device</button>
                </div>
            </form>
        `;

        // Set up form submission
        const form = document.getElementById('addDeviceForm');
        form.addEventListener('submit', (e) => this.handleAddDevice(e));
    }

    // Render location fields for device type
    renderLocationFields(deviceType) {
        return deviceType.locationFields.map((field, index) => {
            let options = '';

            // Add specific options for certain fields
            if (field === 'Placement') {
                options = CONFIG.PLACEMENT_OPTIONS.map(opt =>
                    `<option value="${opt}">${opt}</option>`
                ).join('');
            } else if (field === 'Configuration') {
                options = CONFIG.CONFIGURATION_OPTIONS.map(opt =>
                    `<option value="${opt}">${opt}</option>`
                ).join('');
            }

            const inputType = options ? 'select' : 'text';
            const inputClass = options ? 'form-control form-select' : 'form-control';

            return `
                <div class="form-group">
                    <label class="form-label">${field}</label>
                    <${inputType} name="location_${index}" class="${inputClass}" required>
                        ${options ? options : ''}
                    </${inputType}>
                </div>
            `;
        }).join('');
    }

    // Update location fields when device type changes
    updateLocationFields(deviceTypeValue) {
        const deviceType = ConfigUtils.getDeviceType(deviceTypeValue);
        if (!deviceType) return;

        const container = document.getElementById('location-fields');
        if (container) {
            container.innerHTML = this.renderLocationFields(deviceType);
        }
    }

    // Handle add device form submission
    async handleAddDevice(e) {
        e.preventDefault();

        try {
            UI.setLoading('addDeviceForm', true, 'Adding device...');

            const formData = UI.getFormData('addDeviceForm');
            const deviceType = ConfigUtils.getDeviceType(formData.deviceType);

            // Build location array
            const location = [];
            for (let i = 0; i < deviceType.locationFields.length; i++) {
                location.push(formData[`location_${i}`] || '');
            }

            const deviceData = {
                id: '00-00-00-00-00-00-00-00', // Default ID for new devices
                meta: {
                    location: location,
                    record_type: formData.deviceType
                },
                status: formData.status,
                guid: `frontend-${Date.now()}`
            };

            const response = await AuthManager.makeAuthenticatedRequest(
                ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.CREATE),
                {
                    method: 'POST',
                    body: JSON.stringify(deviceData)
                }
            );

            if (response.ok) {
                const result = await response.json();

                // Add the new device to local state instead of reloading all devices
                if (result.device) {
                    this.devices.push(result.device);
                    this.updateStats();
                    this.renderDevices();
                }

                UI.showNotification('Device added successfully!', 'success');
                UI.hideModal('addDeviceModal');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add device');
            }
        } catch (error) {
            UI.showNotification(`Error adding device: ${error.message}`, 'danger');
        } finally {
            UI.setLoading('addDeviceForm', false);
        }
    }

    // Edit device
    async editDevice(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) {
            UI.showNotification('Device not found', 'danger');
            return;
        }

        // For now, show simple prompt - could be enhanced with modal
        const newStatus = prompt(`Change status for device ${deviceId}:`, device.status);
        if (newStatus && newStatus !== device.status) {
            await this.updateDeviceStatus(deviceId, newStatus);
        }
    }

    // Update device status
    async updateDeviceStatus(deviceId, newStatus) {
        try {
            const deviceIndex = this.devices.findIndex(d => d.id === deviceId);
            if (deviceIndex === -1) return;

            const device = this.devices[deviceIndex];
            const updatedDevice = { ...device, status: newStatus };

            const response = await AuthManager.makeAuthenticatedRequest(
                `${ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.UPDATE)}${deviceId}`,
                {
                    method: 'PUT',
                    body: JSON.stringify(updatedDevice)
                }
            );

            if (response.ok) {
                // Update local state instead of reloading all devices
                this.devices[deviceIndex] = updatedDevice;
                this.updateStats();
                this.renderDevices();

                UI.showNotification(`Device ${deviceId} updated successfully`, 'success');
            } else {
                throw new Error('Failed to update device');
            }
        } catch (error) {
            UI.showNotification(`Error updating device: ${error.message}`, 'danger');
        }
    }

    // Delete device
    async deleteDevice(deviceId) {
        if (!confirm(`Are you sure you want to delete device ${deviceId}?`)) {
            return;
        }

        try {
            const response = await AuthManager.makeAuthenticatedRequest(
                `${ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.DELETE)}${deviceId}`,
                { method: 'DELETE' }
            );

            if (response.ok) {
                // Remove from local state instead of reloading all devices
                this.devices = this.devices.filter(d => d.id !== deviceId);
                this.updateStats();
                this.renderDevices();

                UI.showNotification(`Device ${deviceId} deleted successfully`, 'success');
            } else {
                throw new Error('Failed to delete device');
            }
        } catch (error) {
            UI.showNotification(`Error deleting device: ${error.message}`, 'danger');
        }
    }

    // Hide all modals
    hideModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
        document.body.style.overflow = '';
    }

    // Start auto-refresh
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            if (AuthManager.isAuthenticated()) {
                this.loadDevices();
            }
        }, CONFIG.UI.REFRESH_INTERVAL);
    }

    // Stop auto-refresh
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Run performance benchmark
    async runBenchmark() {
        try {
            UI.updateStatus('Running performance benchmark...', 'info');

            const response = await AuthManager.makeAuthenticatedRequest(
                ConfigUtils.getApiUrl(CONFIG.API.ENDPOINTS.DEVICES.BENCHMARK)
            );

            if (response.ok) {
                const results = await response.json();
                UI.showNotification(`Benchmark completed: ${results.summary}`, 'success');
                return results;
            } else {
                throw new Error('Benchmark failed');
            }
        } catch (error) {
            UI.showNotification(`Benchmark error: ${error.message}`, 'danger');
        }
    }
}

// Create global device manager instance immediately
window.DeviceManager = new DeviceManager();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceManager;
}