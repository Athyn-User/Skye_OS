// Section interactions for Skye OS (Add, Edit, View All functionality)
class SkyeSectionManager {
    constructor() {
        this.activeModal = null;
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
                            <button type="button" class="btn btn-primary" id="saveRecordBtn">Save</button>
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

    handleAddRecord(button) {
        const section = button.dataset.section;
        const table = button.dataset.table;
        
        console.log(`Add record clicked for section: ${section}, table: ${table}`);
        
        // For now, show a placeholder modal
        this.showAddEditModal(section, table, null);
    }

    handleEditRecord(button) {
        const section = button.dataset.section;
        const recordId = button.dataset.recordId;
        
        console.log(`Edit record clicked for section: ${section}, record: ${recordId}`);
        
        // For now, show a placeholder modal
        this.showAddEditModal(section, null, recordId);
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

    showAddEditModal(section, table, recordId) {
        const modal = document.getElementById('recordModal');
        const title = document.getElementById('recordModalTitle');
        const body = document.getElementById('recordModalBody');
        
        if (recordId) {
            title.textContent = `Edit ${section} Record`;
        } else {
            title.textContent = `Add New ${section} Record`;
        }
        
        // Create a simple form based on the section configuration
        const sectionConfig = this.getSectionConfig(section);
        const formHTML = this.createFormHTML(sectionConfig, recordId);
        
        body.innerHTML = formHTML;
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Setup save button
        const saveBtn = document.getElementById('saveRecordBtn');
        saveBtn.onclick = () => this.saveRecord(section, table, recordId);
    }

    async showViewAllModal(section, table) {
        const modal = document.getElementById('viewAllModal');
        const title = document.getElementById('viewAllModalTitle');
        const body = document.getElementById('viewAllModalBody');
        
        title.textContent = `All ${section} Records`;
        body.innerHTML = '<div class="text-center p-4"><div class="loading-spinner"></div><p>Loading...</p></div>';
        
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
        
        // Page numbers (show current and surrounding pages)
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
        body.innerHTML = '<div class="text-center p-4"><div class="loading-spinner"></div><p>Loading...</p></div>';
        
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

    createFormHTML(sectionConfig, recordId) {
        if (!sectionConfig || !sectionConfig.columns) {
            return `
                <div class="alert alert-info">
                    <span class="material-icons">info</span>
                    Form functionality coming soon for this section.
                </div>
            `;
        }
        
        let formHTML = '<form id="recordForm">';
        
        sectionConfig.columns.forEach(column => {
            if (column.db_column === 'id' || column.db_column.endsWith('_id')) {
                return; // Skip ID fields
            }
            
            formHTML += `
                <div class="mb-3">
                    <label for="field_${column.db_column}" class="form-label">
                        ${this.escapeHtml(column.display_name)}
                    </label>
                    <input type="text" 
                           class="form-control" 
                           id="field_${column.db_column}" 
                           name="${column.db_column}"
                           placeholder="Enter ${this.escapeHtml(column.display_name.toLowerCase())}">
                </div>
            `;
        });
        
        formHTML += '</form>';
        
        return formHTML;
    }

    saveRecord(section, table, recordId) {
        const form = document.getElementById('recordForm');
        if (!form) return;
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        console.log('Saving record:', { section, table, recordId, data });
        
        // For now, just show a success message
        this.showNotification(`${recordId ? 'Updated' : 'Created'} record successfully!`, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('recordModal'));
        if (modal) modal.hide();
        
        // TODO: Implement actual save functionality
        // This would involve making an AJAX request to save the data
    }

    getSectionConfig(sectionName) {
        // Try to get config from global SkyeOS object
        if (window.SkyeOS && window.SkyeOS.sectionsConfig && window.SkyeOS.sectionsConfig[sectionName]) {
            return window.SkyeOS.sectionsConfig[sectionName];
        }
        
        // Fallback - create a basic config
        return {
            columns: [
                { db_column: 'name', display_name: 'Name' },
                { db_column: 'description', display_name: 'Description' }
            ]
        };
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
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize section manager
document.addEventListener('DOMContentLoaded', () => {
    window.sectionManager = new SkyeSectionManager();
});