// UI utilities and DOM manipulation helpers

class UIManager {
    constructor() {
        this.loadingStates = new Set();
        this.notifications = [];
    }

    // Show/hide loading state for specific elements
    setLoading(elementId, loading = true, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (loading) {
            this.loadingStates.add(elementId);
            element.disabled = true;

            // Store original content if not already stored
            if (!element.dataset.originalContent) {
                element.dataset.originalContent = element.innerHTML;
            }

            element.innerHTML = `
                <div class="spinner"></div>
                ${message}
            `;
        } else {
            this.loadingStates.delete(elementId);
            element.disabled = false;

            // Restore original content
            if (element.dataset.originalContent) {
                element.innerHTML = element.dataset.originalContent;
                delete element.dataset.originalContent;
            }
        }
    }

    // Show notification/alert
    showNotification(message, type = 'info', duration = CONFIG.UI.NOTIFICATION_TIMEOUT) {
        const notification = {
            id: Date.now(),
            message,
            type,
            duration
        };

        this.notifications.push(notification);
        this.renderNotification(notification);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, duration);
        }

        return notification.id;
    }

    // Remove notification
    removeNotification(notificationId) {
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
        const element = document.getElementById(`notification-${notificationId}`);
        if (element) {
            element.remove();
        }
    }

    // Render notification to DOM
    renderNotification(notification) {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1050;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }

        const element = document.createElement('div');
        element.id = `notification-${notification.id}`;
        element.className = `alert alert-${notification.type}`;
        element.style.cssText = `
            margin-bottom: 10px;
            animation: slideIn 0.3s ease;
            cursor: pointer;
        `;
        element.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${notification.message}</span>
                <button type="button" style="background: none; border: none; font-size: 18px; cursor: pointer;">&times;</button>
            </div>
        `;

        // Add click to dismiss
        element.addEventListener('click', () => {
            this.removeNotification(notification.id);
        });

        container.appendChild(element);
    }

    // Update status message
    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `text-${type}`;
        }
    }

    // Show/hide loading spinner
    showLoadingSpinner(show = true) {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.style.display = show ? 'inline-block' : 'none';
        }
    }

    // Update statistics display
    updateStats(stats) {
        const statElements = {
            'total-devices': stats.totalDevices || 0,
            'active-devices': stats.activeDevices || 0,
            'pending-devices': stats.pendingDevices || 0,
            'total-clusters': stats.totalClusters || 0
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Update device count badge
        const deviceCount = document.getElementById('device-count');
        if (deviceCount) {
            const total = stats.totalDevices || 0;
            deviceCount.textContent = `${total} device${total !== 1 ? 's' : ''}`;
        }
    }

    // Clear container content
    clearContainer(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }

    // Create device card HTML
    createDeviceCard(device) {
        const statusInfo = ConfigUtils.getStatusInfo(device.status);
        const deviceType = ConfigUtils.getDeviceType(device.meta?.record_type);

        return `
            <div class="device-card" data-device-id="${device.id}">
                <div class="device-header">
                    <div>
                        <div class="device-id">${ConfigUtils.formatDeviceId(device.id)}</div>
                        <small class="text-muted">${deviceType?.name || 'Unknown Type'}</small>
                    </div>
                    <span class="device-status ${statusInfo.class}">${statusInfo.label}</span>
                </div>

                <div class="device-location">
                    ${this.renderLocationFields(device.meta?.location || [], deviceType?.locationFields || [])}
                </div>

                <div class="device-actions">
                    <button class="btn btn-sm btn-outline" onclick="DeviceManager.editDevice('${device.id}')">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="DeviceManager.deleteDevice('${device.id}')">
                        Delete
                    </button>
                </div>
            </div>
        `;
    }

    // Render location fields
    renderLocationFields(locationArray, fieldLabels) {
        return locationArray.map((value, index) => {
            const label = fieldLabels[index] || `Field ${index + 1}`;
            return `
                <div class="location-item">
                    <span class="location-label">${label}</span>
                    <span class="location-value">${value || 'N/A'}</span>
                </div>
            `;
        }).join('');
    }

    // Show/hide sections
    showSection(sectionId) {
        document.querySelectorAll('[id$="-section"]').forEach(section => {
            section.classList.add('d-none');
        });

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('d-none');
        }
    }

    // Modal management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    // Form utilities
    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    // Clear form
    clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
    }

    // Populate form with data
    populateForm(formId, data) {
        const form = document.getElementById(formId);
        if (!form) return;

        Object.entries(data).forEach(([key, value]) => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = value;
            }
        });
    }

    // Add event listener with error handling
    addEventHandler(elementId, event, handler) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener(event, async (e) => {
                try {
                    await handler(e);
                } catch (error) {
                    console.error('Event handler error:', error);
                    this.showNotification(`Error: ${error.message}`, 'danger');
                }
            });
        }
    }

    // Format timestamp for display
    formatTimestamp(timestamp) {
        if (!timestamp) return 'N/A';

        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return 'Invalid Date';
        }
    }

    // Debounce function for search/input handling
    debounce(func, wait) {
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
}

// Create global UI manager instance
window.UI = new UIManager();

// Add global styles for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);