class SkyeSectionManager {
    constructor() {
        this.activeModal = null;
        this.fieldCache = {}; // Cache field metadata to avoid repeated API calls
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.setupEventListeners();
        this.createModalHTML();
    }

    setupEventListeners() {
        // Use event delegation for dynamically added buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-record-btn')) {
                this.handleAddRecord(e.target.closest('.add-record-btn'));
            } else if (e.target.closest('.edit-record-btn')) {
                this.handleEditRecord(e.target.closest('.edit-record-btn'));
            } else if (e.target.closest('.view-all-btn')) {
                this.handleViewAll(e.target.closest('.view-all-btn'));
            }
        });
    }

    createModalHTML() {
        // Create modal for add/edit forms
        const modalHTML = `
            <div class="modal fade" id="recordModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="recordModalTitle">Record</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="recordModalBody">
                            <!-- Form content will be inserted here -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveRecordBtn" disabled>
                                <span class="spinner-border spinner-border-sm d-none" role="status"></span>
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="viewAllModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="viewAllModalTitle">All Records</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="viewAllModalBody">
                            <!-- Table content will be inserted here -->
                        </div>
                        <div class="modal-footer">
                            <nav id="viewAllPagination">
                                <!-- Pagination will be inserted here -->
                            </nav>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    async handleAddRecord(button) {
        const section = button.dataset.section;
        const table = button.dataset.table;
        
        console.log(`Add record clicked for section: ${section}, table: ${table}`);
        
        try {
            await this.showAddEditModal(section, table, null);
        } catch (error) {
            console.error('Error showing add modal:', error);
            this.showNotification('Error loading form', 'danger');
        }
    }

    async handleEditRecord(button) {
        const section = button.dataset.section;
        const recordId = button.dataset.recordId;
        
        console.log(`Edit record clicked for section: ${section}, record: ${recordId}`);
        
        try {
            await this.showAddEditModal(section, null, recordId);
        } catch (error) {
            console.error('Error showing edit modal:', error);
            this.showNotification('Error loading record', 'danger');
        }
    }

    async handleViewAll(button) {
        const section = button.dataset.section;
        const table = button.dataset.table;
        
        console.log(`View all clicked for section: ${section}, table: ${table}`);
        
        try {
            await this.showViewAllModal(section, table);
        } catch (error) {
            console.error('Error showing view all modal:', error);
            this.showNotification('Error loading data', 'danger');
        }
    }

    async showAddEditModal(section, table, recordId) {
        const modal = document.getElementById('recordModal');
        const title = document.getElementById('recordModalTitle');
        const body = document.getElementById('recordModalBody');
        const saveBtn = document.getElementById('saveRecordBtn');
        
        // Set modal title
        if (recordId) {
            title.textContent = `Edit ${section} Record`;
        } else {
            title.textContent = `Add New ${section} Record`;
        }
        
        // Show loading state
        body.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading form fields...</p>
            </div>
        `;
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        try {
            // Get field metadata from Django
            const fieldData = await this.getFieldMetadata(section);
            
            let recordData = null;
            if (recordId) {
                // Get existing record data for editing
                recordData = await this.getRecordData(section, recordId);
            }
            
            // Generate form HTML with real fields
            const formHTML = this.createDynamicFormHTML(fieldData, recordData);
            body.innerHTML = formHTML;
            
            // Enable save button and setup event handler
            saveBtn.disabled = false;
            saveBtn.onclick = () => this.saveRecord(section, table, recordId);
            
            // Setup field validation and foreign key loading
            this.setupFormInteractions(fieldData);
            
        } catch (error) {
            console.error('Error loading form:', error);
            body.innerHTML = `
                <div class="alert alert-danger">
                    <span class="material-icons">error</span>
                    Error loading form: ${this.escapeHtml(error.message)}
                </div>
            `;
            saveBtn.disabled = true;
        }
    }

    async getFieldMetadata(section) {
        // Check cache first
        if (this.fieldCache[section]) {
            return this.fieldCache[section];
        }
        
        const response = await fetch(`/main/${window.SkyeOS.pageName}/${section}/fields/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': window.SkyeOS.csrfToken
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load field metadata');
        }
        
        // Cache the result
        this.fieldCache[section] = data;
        return data;
    }

    async getRecordData(section, recordId) {
        const response = await fetch(`/main/${window.SkyeOS.pageName}/${section}/${recordId}/edit/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': window.SkyeOS.csrfToken
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load record data');
        }
        
        return data.data;
    }

    createDynamicFormHTML(fieldData, recordData = null) {
        if (!fieldData.fields || fieldData.fields.length === 0) {
            return `
                <div class="alert alert-info">
                    <span class="material-icons">info</span>
                    No editable fields available for this section.
                </div>
            `;
        }
        
        let formHTML = '<form id="recordForm" class="row g-3">';
        
        fieldData.fields.forEach(field => {
            const currentValue = recordData ? recordData[field.name] : '';
            const fieldHtml = this.generateFieldHTML(field, currentValue);
            formHTML += `<div class="col-md-6">${fieldHtml}</div>`;
        });
        
        formHTML += '</form>';
        return formHTML;
    }

    generateFieldHTML(field, currentValue = '') {
        const fieldId = `field_${field.name}`;
        const required = field.required ? 'required' : '';
        const requiredMark = field.required ? '<span class="text-danger">*</span>' : '';
        
        let inputHTML = '';
        
        switch (field.type) {
            case 'text':
            case 'email':
            case 'url':
                const maxLength = field.max_length ? `maxlength="${field.max_length}"` : '';
                inputHTML = `
                    <input type="${field.type}" 
                           class="form-control" 
                           id="${fieldId}" 
                           name="${field.name}"
                           value="${this.escapeHtml(currentValue)}"
                           placeholder="Enter ${field.label.toLowerCase()}"
                           ${maxLength}
                           ${required}>
                `;
                break;
                
            case 'textarea':
                const maxLengthText = field.max_length ? `maxlength="${field.max_length}"` : '';
                inputHTML = `
                    <textarea class="form-control" 
                              id="${fieldId}" 
                              name="${field.name}"
                              rows="3"
                              placeholder="Enter ${field.label.toLowerCase()}"
                              ${maxLengthText}
                              ${required}>${this.escapeHtml(currentValue)}</textarea>
                `;
                break;
                
            case 'number':
                const step = field.step || '1';
                const maxDigits = field.max_digits ? `data-max-digits="${field.max_digits}"` : '';
                inputHTML = `
                    <input type="number" 
                           class="form-control" 
                           id="${fieldId}" 
                           name="${field.name}"
                           value="${currentValue}"
                           step="${step}"
                           placeholder="Enter ${field.label.toLowerCase()}"
                           ${maxDigits}
                           ${required}>
                `;
                break;
                
            case 'checkbox':
                const checked = currentValue ? 'checked' : '';
                inputHTML = `
                    <div class="form-check">
                        <input type="checkbox" 
                               class="form-check-input" 
                               id="${fieldId}" 
                               name="${field.name}"
                               value="true"
                               ${checked}
                               ${required}>
                        <label class="form-check-label" for="${fieldId}">
                            ${this.escapeHtml(field.label)} ${requiredMark}
                        </label>
                    </div>
                `;
                return inputHTML; // Return early for checkbox (different structure)
                
            case 'select':
                let optionsHTML = `<option value="">${field.empty_label || 'Select an option'}</option>`;
                
                if (field.choices) {
                    // Handle Django model choices
                    field.choices.forEach(choice => {
                        const selected = currentValue == choice[0] ? 'selected' : '';
                        optionsHTML += `<option value="${choice[0]}" ${selected}>${this.escapeHtml(choice[1])}</option>`;
                    });
                } else if (field.options) {
                    // Handle foreign key options
                    field.options.forEach(option => {
                        const selected = currentValue == option.value ? 'selected' : '';
                        optionsHTML += `<option value="${option.value}" ${selected}>${this.escapeHtml(option.label)}</option>`;
                    });
                }
                
                inputHTML = `
                    <select class="form-select" 
                            id="${fieldId}" 
                            name="${field.name}"
                            ${required}
                            data-related-model="${field.related_model || ''}">
                        ${optionsHTML}
                    </select>
                `;
                break;
                
            case 'date':
            case 'datetime-local':
            case 'time':
                inputHTML = `
                    <input type="${field.type}" 
                           class="form-control" 
                           id="${fieldId}" 
                           name="${field.name}"
                           value="${currentValue}"
                           ${required}>
                `;
                break;
                
            default:
                // Fallback to text input
                inputHTML = `
                    <input type="text" 
                           class="form-control" 
                           id="${fieldId}" 
                           name="${field.name}"
                           value="${this.escapeHtml(currentValue)}"
                           placeholder="Enter ${field.label.toLowerCase()}"
                           ${required}>
                `;
        }
        
        // Help text
        const helpText = field.help_text ? `<div class="form-text">${this.escapeHtml(field.help_text)}</div>` : '';
        
        return `
            <label for="${fieldId}" class="form-label">
                ${this.escapeHtml(field.label)} ${requiredMark}
            </label>
            ${inputHTML}
            ${helpText}
        `;
    }

    setupFormInteractions(fieldData) {
        // Setup form validation
        const form = document.getElementById('recordForm');
        if (form) {
            form.addEventListener('input', () => this.validateForm());
            form.addEventListener('change', () => this.validateForm());
        }
        
        // Setup dynamic foreign key loading if needed
        fieldData.fields.forEach(field => {
            if (field.type === 'select' && field.related_model) {
                this.setupForeignKeyField(field);
            }
        });
    }

    setupForeignKeyField(field) {
        const select = document.getElementById(`field_${field.name}`);
        if (select && field.options && field.options.length === 0) {
            // If no options loaded, try to load them dynamically
            this.loadForeignKeyOptions(field.name, field.related_model);
        }
    }

    async loadForeignKeyOptions(fieldName, relatedModel) {
        try {
            const response = await fetch(`/main/${window.SkyeOS.pageName}/fk-options/${fieldName}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.SkyeOS.csrfToken
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const select = document.getElementById(`field_${fieldName}`);
                    if (select) {
                        // Clear existing options except the first (empty) one
                        while (select.children.length > 1) {
                            select.removeChild(select.lastChild);
                        }
                        
                        // Add new options
                        data.options.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option.value;
                            optionElement.textContent = option.label;
                            select.appendChild(optionElement);
                        });
                    }
                }
            }
        } catch (error) {
            console.warn(`Could not load options for ${fieldName}:`, error);
        }
    }

    validateForm() {
        const form = document.getElementById('recordForm');
        const saveBtn = document.getElementById('saveRecordBtn');
        
        if (!form || !saveBtn) return;
        
        const isValid = form.checkValidity();
        saveBtn.disabled = !isValid;
        
        // Add visual feedback for invalid fields
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.checkValidity()) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
            }
        });
    }

    async saveRecord(section, table, recordId) {
        const form = document.getElementById('recordForm');
        const saveBtn = document.getElementById('saveRecordBtn');
        const spinner = saveBtn.querySelector('.spinner-border');
        
        if (!form || !form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Show loading state
        saveBtn.disabled = true;
        spinner?.classList.remove('d-none');
        
        try {
            const formData = new FormData(form);
            const data = {};
            
            // Convert FormData to regular object, handling checkboxes
            for (const [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Handle unchecked checkboxes (they don't appear in FormData)
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                if (!checkbox.checked) {
                    data[checkbox.name] = false;
                }
            });
            
            const url = recordId 
                ? `/main/${window.SkyeOS.pageName}/${section}/${recordId}/edit/`
                : `/main/${window.SkyeOS.pageName}/${section}/add/`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.SkyeOS.csrfToken
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(
                    `${recordId ? 'Updated' : 'Created'} record successfully!`, 
                    'success'
                );
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('recordModal'));
                if (modal) modal.hide();
                
                // Refresh the section data
                this.refreshSectionData(section);
                
            } else {
                throw new Error(result.error || 'Failed to save record');
            }
            
        } catch (error) {
            console.error('Error saving record:', error);
            this.showNotification(`Error saving record: ${error.message}`, 'danger');
        } finally {
            // Hide loading state
            saveBtn.disabled = false;
            spinner?.classList.add('d-none');
        }
    }

    async refreshSectionData(section) {
        // Find the section container and refresh its data
        const sectionContainer = document.querySelector(`[data-section="${section}"]`);
        if (sectionContainer) {
            try {
                const response = await fetch(`/main/${window.SkyeOS.pageName}/${section}/data/`, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': window.SkyeOS.csrfToken
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        // Update the section with new data
                        // This would require updating the section rendering logic
                        console.log('Section data refreshed:', section);
                    }
                }
            } catch (error) {
                console.warn('Could not refresh section data:', error);
            }
        }
    }

    async showViewAllModal(section, table) {
        const modal = document.getElementById('viewAllModal');
        const title = document.getElementById('viewAllModalTitle');
        const body = document.getElementById('viewAllModalBody');
        
        title.textContent = `All ${section} Records`;
        body.innerHTML = '<div class="text-center p-4"><div class="spinner-border"></div><p>Loading...</p></div>';
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        try {
            const response = await fetch(`/main/${window.SkyeOS.pageName}/${section}/data/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.SkyeOS.csrfToken
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.renderViewAllTable(data, section);
            } else {
                throw new Error(data.error || 'Failed to load data');
            }
        } catch (error) {
            console.error('Error loading view all data:', error);
            body.innerHTML = `
                <div class="alert alert-danger">
                    <span class="material-icons">error</span>
                    Error loading data: ${this.escapeHtml(error.message)}
                </div>
            `;
        }
    }

    renderViewAllTable(data, section) {
        const body = document.getElementById('viewAllModalBody');
        const config = data.config;
        const records = data.data;
        const pagination = data.pagination;
        
        if (!records || records.length === 0) {
            body.innerHTML = `
                <div class="text-center p-4">
                    <span class="material-icons" style="font-size: 48px; color: #ccc;">inbox</span>
                    <h6 class="mt-2">No records found</h6>
                    <p class="text-muted">This section doesn't contain any data yet.</p>
                </div>
            `;
            return;
        }
        
        // Create table
        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            ${config.columns.map(col => `<th>${this.escapeHtml(col.display_name)}</th>`).join('')}
                            ${config.edit_button ? '<th>Actions</th>' : ''}
                        </tr>
                    </thead>
                    <tbody>
                        ${records.map(record => `
                            <tr>
                                ${config.columns.map(col => `
                                    <td>${record[col.db_column] ? this.escapeHtml(record[col.db_column]) : '<span class="text-muted">—</span>'}</td>
                                `).join('')}
                                ${config.edit_button ? `
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary edit-record-btn"
                                                data-section="${section}" 
                                                data-record-id="${record.pk}">
                                            <span class="material-icons">edit</span>
                                        </button>
                                    </td>
                                ` : ''}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        body.innerHTML = tableHTML;
        
        // Setup pagination if needed
        if (pagination && pagination.total_pages > 1) {
            this.setupViewAllPagination(pagination, section);
        }
    }

    setupViewAllPagination(pagination, section) {
        const paginationContainer = document.getElementById('viewAllPagination');
        
        let paginationHTML = '<ul class="pagination pagination-sm">';
        
        // Previous button
        if (pagination.has_previous) {
            paginationHTML += `
                <li class="page-item">
                    <button class="page-link" onclick="window.sectionManager.loadViewAllPage(${pagination.current_page - 1}, '${section}')">
                        Previous
                    </button>
                </li>
            `;
        }
        
        // Page numbers
        const startPage = Math.max(1, pagination.current_page - 2);
        const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === pagination.current_page ? 'active' : ''}">
                    <button class="page-link" onclick="window.sectionManager.loadViewAllPage(${i}, '${section}')">
                        ${i}
                    </button>
                </li>
            `;
        }
        
        // Next button
        if (pagination.has_next) {
            paginationHTML += `
                <li class="page-item">
                    <button class="page-link" onclick="window.sectionManager.loadViewAllPage(${pagination.current_page + 1}, '${section}')">
                        Next
                    </button>
                </li>
            `;
        }
        
        paginationHTML += '</ul>';
        paginationContainer.innerHTML = paginationHTML;
    }

    async loadViewAllPage(page, section) {
        const body = document.getElementById('viewAllModalBody');
        body.innerHTML = '<div class="text-center p-4"><div class="spinner-border"></div><p>Loading...</p></div>';
        
        try {
            const response = await fetch(`/main/${window.SkyeOS.pageName}/${section}/data/?page=${page}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': window.SkyeOS.csrfToken
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.renderViewAllTable(data, section);
            } else {
                throw new Error(data.error || 'Failed to load data');
            }
        } catch (error) {
            console.error('Error loading page:', error);
            body.innerHTML = `
                <div class="alert alert-danger">
                    Error loading page: ${this.escapeHtml(error.message)}
                </div>
            `;
        }
    }

    showNotification(message, type = 'info') {
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                ${this.escapeHtml(message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHTML);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert.position-fixed');
            alerts.forEach(alert => {
                if (alert.parentNode) {
                    alert.remove();
                }
            });
        }, 3000);
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }
}

// Initialize section manager
document.addEventListener('DOMContentLoaded', () => {
    window.sectionManager = new SkyeSectionManager();
});