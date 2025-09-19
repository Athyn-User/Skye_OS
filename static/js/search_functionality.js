// Search functionality for Skye OS
class SkyeSearchManager {
    constructor() {
        this.searchInput = null;
        this.searchButton = null;
        this.clearButton = null;
        this.searchResults = null;
        this.searchResultsContent = null;
        this.closeSearchButton = null;
        this.searchTimeout = null;
        this.isSearching = false;
        
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
        this.searchInput = document.getElementById('globalSearch');
        this.searchButton = document.getElementById('searchButton');
        this.clearButton = document.getElementById('clearSearch');
        this.searchResults = document.getElementById('searchResults');
        this.searchResultsContent = document.getElementById('searchResultsContent');
        this.closeSearchButton = document.getElementById('closeSearch');

        if (!this.searchInput) return;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }

            // Show/hide clear button
            this.toggleClearButton(query.length > 0);

            if (query.length >= 2) {
                // Debounce search
                this.searchTimeout = setTimeout(() => {
                    this.performSearch(query);
                }, 300);
            } else if (query.length === 0) {
                this.hideSearchResults();
            }
        });

        // Enter key to search
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.searchInput.value.trim();
                if (query.length >= 2) {
                    this.performSearch(query);
                }
            }
        });

        // Search button click
        if (this.searchButton) {
            this.searchButton.addEventListener('click', () => {
                const query = this.searchInput.value.trim();
                if (query.length >= 2) {
                    this.performSearch(query);
                }
            });
        }

        // Clear button click
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Close search results
        if (this.closeSearchButton) {
            this.closeSearchButton.addEventListener('click', () => {
                this.hideSearchResults();
            });
        }

        // Click outside to close search results
        document.addEventListener('click', (e) => {
            if (this.searchResults && this.searchResults.classList.contains('show')) {
                if (!this.searchResults.contains(e.target) && 
                    !this.searchInput.contains(e.target) && 
                    !this.searchButton.contains(e.target)) {
                    this.hideSearchResults();
                }
            }
        });
    }

    toggleClearButton(show) {
        if (this.clearButton) {
            this.clearButton.style.display = show ? 'block' : 'none';
        }
    }

    async performSearch(query) {
        if (this.isSearching || !query || query.length < 2) return;

        this.isSearching = true;
        this.showSearchLoading();

        try {
            console.log(`Searching for: "${query}"`);
            
            const response = await fetch(`/main/${window.SkyeOS.pageName}/search/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.SkyeOS.csrfToken
                },
                body: JSON.stringify({
                    query: query
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results, query);
            } else {
                this.showSearchError(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError('Network error during search');
        } finally {
            this.isSearching = false;
        }
    }

    showSearchLoading() {
        if (!this.searchResultsContent) return;

        this.searchResultsContent.innerHTML = `
            <div class="text-center p-4">
                <div class="loading-spinner"></div>
                <p class="loading-text">Searching...</p>
            </div>
        `;
        
        this.showSearchResults();
    }

    displaySearchResults(results, query) {
        if (!this.searchResultsContent) return;

        const resultCount = Object.keys(results).length;
        
        if (resultCount === 0) {
            this.searchResultsContent.innerHTML = `
                <div class="text-center p-4">
                    <span class="material-icons text-muted" style="font-size: 48px;">search_off</span>
                    <h6 class="mt-2">No results found</h6>
                    <p class="text-muted">No matches for "${this.escapeHtml(query)}"</p>
                </div>
            `;
        } else {
            let resultsHtml = `
                <div class="search-results-header p-3 border-bottom">
                    <h6 class="mb-0">Found ${resultCount} sections with matches for "${this.escapeHtml(query)}"</h6>
                </div>
            `;

            Object.entries(results).forEach(([sectionName, sectionData]) => {
                resultsHtml += this.createSearchResultSection(sectionName, sectionData, query);
            });

            this.searchResultsContent.innerHTML = resultsHtml;
        }

        this.showSearchResults();
    }

    createSearchResultSection(sectionName, sectionData, query) {
        const config = sectionData.config;
        const data = sectionData.data;
        const count = sectionData.count;

        let recordsHtml = '';
        data.slice(0, 5).forEach(record => { // Show max 5 results per section
            const primaryField = config.columns[0]?.db_column || 'pk';
            const primaryValue = record[primaryField] || record.pk;
            
            recordsHtml += `
                <div class="search-result-item d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <strong>${this.escapeHtml(primaryValue)}</strong>
                        <div class="small text-muted">
                            ${config.columns.slice(1, 3).map(col => {
                                const value = record[col.db_column];
                                return value ? `${col.display_name}: ${this.escapeHtml(value)}` : '';
                            }).filter(Boolean).join(' • ')}
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="window.skyeSearch.goToSection('${sectionName}', ${record.pk})">
                        <span class="material-icons">visibility</span>
                    </button>
                </div>
            `;
        });

        if (count > 5) {
            recordsHtml += `
                <div class="text-center py-2">
                    <button class="btn btn-sm btn-link" 
                            onclick="window.skyeSearch.viewAllResults('${sectionName}')">
                        View all ${count} results in ${sectionName}
                    </button>
                </div>
            `;
        }

        return `
            <div class="search-result-section">
                <div class="search-result-title d-flex align-items-center">
                    <span class="material-icons me-2">${config.icon}</span>
                    <span>${this.escapeHtml(sectionName)}</span>
                    <span class="search-result-count">${count} matches</span>
                </div>
                <div class="search-result-records">
                    ${recordsHtml}
                </div>
            </div>
        `;
    }

    showSearchResults() {
        if (this.searchResults) {
            this.searchResults.classList.add('show');
        }
    }

    hideSearchResults() {
        if (this.searchResults) {
            this.searchResults.classList.remove('show');
        }
    }

    showSearchError(message) {
        if (!this.searchResultsContent) return;

        this.searchResultsContent.innerHTML = `
            <div class="text-center p-4">
                <span class="material-icons text-danger" style="font-size: 48px;">error</span>
                <h6 class="mt-2 text-danger">Search Error</h6>
                <p class="text-muted">${this.escapeHtml(message)}</p>
            </div>
        `;
        
        this.showSearchResults();
    }

    clearSearch() {
        this.searchInput.value = '';
        this.toggleClearButton(false);
        this.hideSearchResults();
        
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
    }

    goToSection(sectionName, recordId = null) {
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        const sectionElement = document.getElementById(`section-${sectionId}`);
        
        if (sectionElement) {
            // Hide search results first
            this.hideSearchResults();
            
            // Scroll to section
            sectionElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            
            // Update sidebar active item
            const sidebarItem = document.querySelector(`.sidebar-item[href="#section-${sectionId}"]`);
            if (sidebarItem && window.skyeLoader) {
                window.skyeLoader.updateActiveSidebarItem(sidebarItem);
            }
            
            // Highlight the record if specified
            if (recordId) {
                setTimeout(() => {
                    const recordRow = sectionElement.querySelector(`tr[data-record-id="${recordId}"]`);
                    if (recordRow) {
                        recordRow.classList.add('table-warning');
                        setTimeout(() => {
                            recordRow.classList.remove('table-warning');
                        }, 3000);
                    }
                }, 500);
            }
        } else {
            console.warn(`Section ${sectionName} not found in DOM`);
        }
    }

    viewAllResults(sectionName) {
        // Navigate to section and show all data
        this.goToSection(sectionName);
        
        // Trigger view all functionality if available
        const sectionId = sectionName.toLowerCase().replace(/\s+/g, '-');
        const sectionElement = document.getElementById(`section-${sectionId}`);
        
        if (sectionElement) {
            const viewAllButton = sectionElement.querySelector('.view-all-btn');
            if (viewAllButton) {
                setTimeout(() => {
                    viewAllButton.click();
                }, 1000);
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize search manager
document.addEventListener('DOMContentLoaded', () => {
    window.skyeSearch = new SkyeSearchManager();
});