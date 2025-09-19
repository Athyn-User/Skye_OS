// Enhanced Progressive Loader for Skye OS
class SkyeProgressiveLoader {
    constructor() {
        this.isLoading = false;
        this.loadingTrigger = null;
        this.observer = null;
        this.sectionsContainer = null;
        this.sidebarContent = null;
        this.sidebarLoading = null;
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.loadingTrigger = document.getElementById('loadingTrigger');
        this.sectionsContainer = document.getElementById('sectionsContainer');
        this.sidebarContent = document.getElementById('sidebarContent');
        this.sidebarLoading = document.getElementById('sidebarLoading');

        if (!this.loadingTrigger || !window.SkyeOS.hasMoreSections) {
            console.log('Progressive loading not needed - all sections loaded or no trigger element');
            return;
        }

        this.setupIntersectionObserver();
        this.setupSidebarScrolling();
        
        // Auto-load remaining sections if we have very few initially
        if (window.SkyeOS.nextSectionIndex <= 3) {
            setTimeout(() => this.loadMoreSections(), 1000);
        }
    }

    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading && window.SkyeOS.hasMoreSections) {
                    console.log('Loading trigger visible, loading more sections...');
                    this.loadMoreSections();
                }
            });
        }, options);

        this.observer.observe(this.loadingTrigger);
    }

    setupSidebarScrolling() {
        // Add smooth scrolling to sidebar links
        const sidebarLinks = document.querySelectorAll('.sidebar-item[href^="#"]');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update active sidebar item
                    this.updateActiveSidebarItem(link);
                }
            });
        });
    }

    updateActiveSidebarItem(activeLink) {
        // Remove active class from all sidebar items
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked item
        activeLink.classList.add('active');
    }

    async loadMoreSections() {
        if (this.isLoading || !window.SkyeOS.hasMoreSections) {
            return;
        }

        this.isLoading = true;
        this.showSidebarLoading(true);

        try {
            console.log(`Loading sections starting from index: ${window.SkyeOS.nextSectionIndex}`);
            
            const response = await fetch(`/main/${window.SkyeOS.pageName}/load-more/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.SkyeOS.csrfToken
                },
                body: JSON.stringify({
                    start_index: window.SkyeOS.nextSectionIndex
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                console.log(`Loaded ${Object.keys(data.sections).length} new sections`);
                await this.appendSections(data.sections);
                
                // Update global state
                window.SkyeOS.hasMoreSections = data.has_more;
                window.SkyeOS.nextSectionIndex = data.next_index;

                // Remove loading trigger if no more sections
                if (!data.has_more && this.loadingTrigger) {
                    this.loadingTrigger.remove();
                    this.loadingTrigger = null;
                    if (this.observer) {
                        this.observer.disconnect();
                    }
                    console.log('All sections loaded!');
                }
            } else {
                console.error('Failed to load more sections:', data.error);
                this.showError('Failed to load more sections. Please refresh the page.');
            }
        } catch (error) {
            console.error('Error loading more sections:', error);
            this.showError('Network error loading sections. Please check your connection.');
        } finally {
            this.isLoading = false;
            this.showSidebarLoading(false);
        }
    }

    async appendSections(sections) {
        // Add new sections to the DOM
        for (const [sectionName, sectionData] of Object.entries(sections)) {
            const sectionHtml = this.createSectionHTML(sectionName, sectionData);
            
            // Insert before the loading trigger
            if (this.loadingTrigger && this.loadingTrigger.parentNode) {
                this.loadingTrigger.insertAdjacentHTML('beforebegin', sectionHtml);
            } else {
                // Fallback: append to sections container
                this.sectionsContainer.insertAdjacentHTML('beforeend', sectionHtml);
            }
            
            // Add to sidebar
            this.addSidebarItem(sectionName, sectionData.config);
        }

        // Setup interactions for new sections
        this.setupSectionInteractions();
    }

    createSectionHTML(sectionName, sectionData) {
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        const hasActions = sectionData.config.edit_button || sectionData.config.add_button;
        
        let tableHTML = '';
        
        if (sectionData.error) {
            tableHTML = `
                <div class="alert alert-warning" role="alert">
                    <span class="material-icons">error</span>
                    Error: ${this.escapeHtml(sectionData.error)}
                </div>
            `;
        } else if (sectionData.data && sectionData.data.length > 0) {
            const actionsHeader = hasActions ? '<th class="actions-column">Actions</th>' : '';
            const columnHeaders = sectionData.config.columns
                .map(col => `<th>${this.escapeHtml(col.display_name)}</th>`)
                .join('');
            
            const rows = sectionData.data.map(record => {
                const cells = sectionData.config.columns
                    .map(col => {
                        const value = record[col.db_column];
                        return `<td>${value ? this.escapeHtml(value) : '<span class="text-muted">—</span>'}</td>`;
                    })
                    .join('');
                
                const actionsCell = hasActions ? `
                    <td class="actions-column">
                        ${sectionData.config.edit_button ? `
                            <button class="btn btn-sm btn-outline-primary edit-record-btn"
                                    data-section="${this.escapeHtml(sectionName)}"
                                    data-record-id="${record.pk}">
                                <span class="material-icons">edit</span>
                            </button>
                        ` : ''}
                    </td>
                ` : '';
                
                return `<tr data-record-id="${record.pk}">${cells}${actionsCell}</tr>`;
            }).join('');
            
            tableHTML = `
                <div class="table-responsive">
                    <table class="table table-hover vertex-table">
                        <thead>
                            <tr>${columnHeaders}${actionsHeader}</tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
                ${sectionData.total_count > sectionData.data.length ? `
                    <div class="section-footer">
                        <small class="text-muted">
                            Showing ${sectionData.data.length} of ${sectionData.total_count} records
                        </small>
                    </div>
                ` : ''}
            `;
        } else {
            tableHTML = `
                <div class="empty-state">
                    <span class="material-icons empty-icon">inbox</span>
                    <p class="text-muted">No data available</p>
                    ${sectionData.config.add_button ? `
                        <button type="button" class="btn btn-primary add-record-btn"
                                data-section="${this.escapeHtml(sectionName)}" 
                                data-table="${this.escapeHtml(sectionData.config.table)}">
                            <span class="material-icons">add</span>
                            Add First Record
                        </button>
                    ` : ''}
                </div>
            `;
        }
        
        return `
            <section class="section-container" id="section-${sectionId}" data-section="${this.escapeHtml(sectionName)}">
                <div class="section-header">
                    <div class="section-title">
                        <span class="material-icons section-icon">${sectionData.config.icon}</span>
                        <h4>${this.escapeHtml(sectionName)}</h4>
                        <span class="section-count">(${sectionData.total_count} total)</span>
                    </div>
                    
                    <div class="section-actions">
                        ${sectionData.config.add_button ? `
                            <button type="button" class="btn btn-primary btn-sm add-record-btn"
                                    data-section="${this.escapeHtml(sectionName)}" 
                                    data-table="${this.escapeHtml(sectionData.config.table)}">
                                <span class="material-icons">add</span>
                                Add New
                            </button>
                        ` : ''}
                        
                        <button type="button" class="btn btn-outline-primary btn-sm view-all-btn"
                                data-section="${this.escapeHtml(sectionName)}" 
                                data-table="${this.escapeHtml(sectionData.config.table)}">
                            <span class="material-icons">view_list</span>
                            View All
                        </button>
                    </div>
                </div>
                <div class="section-content">
                    ${tableHTML}
                </div>
            </section>
        `;
    }

    addSidebarItem(sectionName, config) {
        if (!this.sidebarContent) return;
        
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        
        const itemHTML = `
            <a href="#section-${sectionId}" class="sidebar-item" data-section="${this.escapeHtml(sectionName)}">
                <span class="material-icons sidebar-icon">${config.icon}</span>
                <span class="sidebar-text">${this.escapeHtml(sectionName)}</span>
            </a>
        `;
        
        this.sidebarContent.insertAdjacentHTML('beforeend', itemHTML);
        
        // Setup scrolling for the new item
        const newItem = this.sidebarContent.lastElementChild;
        newItem.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = newItem.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                this.updateActiveSidebarItem(newItem);
            }
        });
    }

    setupSectionInteractions() {
        // Setup edit button clicks for newly added sections
        document.querySelectorAll('.edit-record-btn:not([data-initialized])').forEach(btn => {
            btn.setAttribute('data-initialized', 'true');
            btn.addEventListener('click', (e) => {
                const section = e.target.closest('[data-section]').dataset.section;
                const recordId = e.target.closest('[data-record-id]').dataset.recordId;
                console.log(`Edit clicked for section: ${section}, record: ${recordId}`);
                // Add your edit functionality here
            });
        });

        // Setup add button clicks for newly added sections
        document.querySelectorAll('.add-record-btn:not([data-initialized])').forEach(btn => {
            btn.setAttribute('data-initialized', 'true');
            btn.addEventListener('click', (e) => {
                const section = btn.dataset.section;
                const table = btn.dataset.table;
                console.log(`Add clicked for section: ${section}, table: ${table}`);
                // Add your add functionality here
            });
        });

        // Setup view all button clicks for newly added sections
        document.querySelectorAll('.view-all-btn:not([data-initialized])').forEach(btn => {
            btn.setAttribute('data-initialized', 'true');
            btn.addEventListener('click', (e) => {
                const section = btn.dataset.section;
                const table = btn.dataset.table;
                console.log(`View all clicked for section: ${section}, table: ${table}`);
                // Add your view all functionality here
            });
        });
    }

    showSidebarLoading(show) {
        if (this.sidebarLoading) {
            this.sidebarLoading.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <span class="material-icons">error</span>
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of content area
        const contentArea = document.getElementById('contentArea');
        if (contentArea) {
            contentArea.insertBefore(errorDiv, contentArea.firstChild);
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Skye Progressive Loader...');
    window.skyeLoader = new SkyeProgressiveLoader();
});