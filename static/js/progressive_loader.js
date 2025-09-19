// Progressive loading functionality
class SkyeProgressiveLoader {
    constructor() {
        this.isLoading = false;
        this.setupIntersectionObserver();
    }

    setupIntersectionObserver() {
        const loadingTrigger = document.getElementById('loadingTrigger');
        if (!loadingTrigger) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading && window.SkyeOS.hasMoreSections) {
                    this.loadMoreSections();
                }
            });
        }, {
            rootMargin: '200px'
        });

        observer.observe(loadingTrigger);
    }

    async loadMoreSections() {
        if (this.isLoading || !window.SkyeOS.hasMoreSections) return;

        this.isLoading = true;
        const loadingElement = document.getElementById('loadingMore');
        
        try {
            const response = await fetch(`/main/${window.SkyeOS.pageName}/load-more/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    start_index: window.SkyeOS.nextSectionIndex
                })
            });

            const data = await response.json();

            if (data.success) {
                this.appendSections(data.sections);
                window.SkyeOS.hasMoreSections = data.has_more;
                window.SkyeOS.nextSectionIndex = data.next_index;

                if (!data.has_more) {
                    loadingElement?.remove();
                }
            } else {
                console.error('Failed to load more sections:', data.error);
            }
        } catch (error) {
            console.error('Error loading more sections:', error);
        } finally {
            this.isLoading = false;
        }
    }

    appendSections(sections) {
        const container = document.getElementById('sectionsContainer');
        
        Object.entries(sections).forEach(([sectionName, sectionData]) => {
            const sectionHtml = this.createSectionHTML(sectionName, sectionData);
            container.insertAdjacentHTML('beforeend', sectionHtml);
            
            // Add to sidebar
            this.addSidebarItem(sectionName, sectionData.config);
        });
    }

    createSectionHTML(sectionName, sectionData) {
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        
        let tableHTML = '';
        if (sectionData.error) {
            tableHTML = `
                <div class="alert alert-warning" role="alert">
                    <span class="material-icons">error</span>
                    Error: ${sectionData.error}
                </div>
            `;
        } else if (sectionData.data && sectionData.data.length > 0) {
            tableHTML = `
                <div class="table-responsive">
                    <table class="table table-hover vertex-table">
                        <thead>
                            <tr>
                                ${sectionData.config.columns.map(col => `<th>${col.display_name}</th>`).join('')}
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${sectionData.data.map(record => `
                                <tr>
                                    ${sectionData.config.columns.map(col => `
                                        <td>${record[col.db_column] || '—'}</td>
                                    `).join('')}
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary">
                                            <span class="material-icons">edit</span>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            tableHTML = `
                <div class="empty-state">
                    <span class="material-icons empty-icon">inbox</span>
                    <p class="text-muted">No data available</p>
                </div>
            `;
        }
        
        return `
            <section class="section-container" id="section-${sectionId}" data-section="${sectionName}">
                <div class="section-header">
                    <div class="section-title">
                        <span class="material-icons section-icon">${sectionData.config.icon}</span>
                        <h4>${sectionName}</h4>
                        <span class="section-count">(${sectionData.total_count} total)</span>
                    </div>
                    
                    <div class="section-actions">
                        <button type="button" class="btn btn-primary btn-sm">
                            <span class="material-icons">add</span>
                            Add New
                        </button>
                        <button type="button" class="btn btn-outline-primary btn-sm">
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
        const sidebar = document.querySelector('.sidebar-content');
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        
        const itemHTML = `
            <a href="#section-${sectionId}" class="sidebar-item" data-section="${sectionName}">
                <span class="material-icons sidebar-icon">${config.icon}</span>
                <span class="sidebar-text">${sectionName}</span>
            </a>
        `;
        
        sidebar.insertAdjacentHTML('beforeend', itemHTML);
    }

    getCSRFToken() {
        return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SkyeProgressiveLoader();
});