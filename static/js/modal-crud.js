// Modal CRUD functionality for Skye OS
// Handles modal opening, form submission, and table updates

class ModalCRUD {
    constructor() {
        this.currentModal = null;
        this.init();
    }

    init() {
        // Add click handlers for edit buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit-modal')) {
                e.preventDefault();
                this.openEditModal(e.target);
            }
            
            if (e.target.classList.contains('modal-close') || 
                e.target.classList.contains('btn-cancel')) {
                e.preventDefault();
                this.closeModal();
            }
        });

        // Close modal when clicking overlay
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeModal();
            }
        });

        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('modal-form')) {
                e.preventDefault();
                this.submitForm(e.target);
            }
        });
    }

    openEditModal(button) {
        const modelName = button.dataset.model;
        const objectId = button.dataset.id;
        
        if (!modelName || !objectId) {
            console.error('Missing model name or object ID');
            return;
        }

        // Show loading state
        this.showLoading(button);

        // Build AJAX URL
        const url = `/ajax/${modelName}/${objectId}/edit/`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading(button);
            
            if (data.success) {
                this.showModal(data.html);
            } else {
                this.showError('Failed to load edit form: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            this.hideLoading(button);
            console.error('Error loading modal:', error);
            this.showError('Failed to load edit form. Please try again.');
        });
    }

    submitForm(form) {
        const formData = new FormData(form);
        const url = form.action;

        // Show loading state on submit button
        const submitBtn = form.querySelector('.btn-submit');
        this.showLoading(submitBtn);

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading(submitBtn);
            
            if (data.success) {
                this.handleSuccess(data);
            } else {
                this.handleFormErrors(data.errors, data.html);
            }
        })
        .catch(error => {
            this.hideLoading(submitBtn);
            console.error('Error submitting form:', error);
            this.showError('Failed to save changes. Please try again.');
        });
    }

    handleSuccess(data) {
        // Show success message
        this.showSuccess(data.message || 'Changes saved successfully!');
        
        // Update the table row if new HTML is provided
        if (data.row_html && data.object_id) {
            this.updateTableRow(data.object_id, data.row_html);
        }
        
        // Close modal after a brief delay
        setTimeout(() => {
            this.closeModal();
        }, 1500);
    }

    handleFormErrors(errors, newFormHtml) {
        if (newFormHtml) {
            // Replace form with error version
            const modalBody = this.currentModal.querySelector('.modal-body');
            modalBody.innerHTML = newFormHtml;
        } else if (errors) {
            // Display errors
            this.displayFormErrors(errors);
        }
    }

    updateTableRow(objectId, newRowHtml) {
        // Find the table row and update it
        const tableRows = document.querySelectorAll('tbody tr');
        
        for (let row of tableRows) {
            const editBtn = row.querySelector('.btn-edit-modal');
            if (editBtn && editBtn.dataset.id === objectId.toString()) {
                row.innerHTML = newRowHtml;
                
                // Add a brief highlight effect
                row.style.backgroundColor = '#f0f8ff';
                setTimeout(() => {
                    row.style.backgroundColor = '';
                }, 2000);
                break;
            }
        }
    }

    showModal(html) {
        // Remove any existing modal
        this.closeModal();

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = html;

        // Add to page
        document.body.appendChild(overlay);
        this.currentModal = overlay;

        // Show with animation
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);

        // Focus first input
        const firstInput = overlay.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 300);
        }
    }

    closeModal() {
        if (this.currentModal) {
            this.currentModal.classList.remove('show');
            
            setTimeout(() => {
                if (this.currentModal && this.currentModal.parentNode) {
                    this.currentModal.parentNode.removeChild(this.currentModal);
                }
                this.currentModal = null;
            }, 300);
        }
    }

    showLoading(element) {
        if (element) {
            element.disabled = true;
            element.classList.add('loading');
            
            // Add spinner if it's a button
            if (element.tagName === 'BUTTON') {
                const originalText = element.innerHTML;
                element.dataset.originalText = originalText;
                element.innerHTML = '<span class="spinner"></span>Loading...';
            }
        }
    }

    hideLoading(element) {
        if (element) {
            element.disabled = false;
            element.classList.remove('loading');
            
            // Restore original text if it's a button
            if (element.tagName === 'BUTTON' && element.dataset.originalText) {
                element.innerHTML = element.dataset.originalText;
                delete element.dataset.originalText;
            }
        }
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        // Create toast-style message
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span>${message}</span>
                <button class="toast-close">&times;</button>
            </div>
        `;

        // Add styles
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideInRight 0.3s ease-out;
            max-width: 400px;
        `;

        // Add animation styles to head if not exists
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .toast-content { display: flex; align-items: center; justify-content: space-between; width: 100%; }
                .toast-close { background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: 12px; }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);

        // Manual close
        toast.querySelector('.toast-close').addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }

    displayFormErrors(errors) {
        // Clear existing errors
        const existingErrors = this.currentModal.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());

        const errorInputs = this.currentModal.querySelectorAll('.form-control.error');
        errorInputs.forEach(input => input.classList.remove('error'));

        // Display new errors
        for (const [fieldName, fieldErrors] of Object.entries(errors)) {
            const field = this.currentModal.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('error');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = Array.isArray(fieldErrors) ? fieldErrors[0] : fieldErrors;
                
                field.parentNode.appendChild(errorDiv);
            }
        }
    }

    getCSRFToken() {
        // Get CSRF token from cookie or meta tag
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) {
            return token.value;
        }
        
        // Fallback: get from cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
            
        return cookieValue || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.modalCRUD = new ModalCRUD();
    console.log('Modal CRUD system initialized');
});