// Path: static/js/sidebar.js

/**
 * Sidebar Management Script
 * Handles collapse/expand functionality with localStorage persistence
 */

(function() {
    'use strict';
    
    // Constants
    const STORAGE_KEY = 'sidebar-collapsed';
    const MOBILE_BREAKPOINT = 768;
    
    // DOM elements
    let sidebar;
    let overlay;
    let mainContent;
    
    /**
     * Initialize sidebar functionality
     */
    function initSidebar() {
        sidebar = document.getElementById('sidebar');
        overlay = document.getElementById('sidebar-overlay');
        mainContent = document.querySelector('.main-content');
        
        if (!sidebar) return;
        
        // Load saved state from localStorage
        loadSidebarState();
        
        // Add data-tooltip attributes for collapsed state
        addTooltips();
        
        // Handle window resize
        window.addEventListener('resize', handleResize);
        
        // Add keyboard shortcut (Ctrl/Cmd + B)
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                toggleSidebar();
            }
        });
        
        // Initialize on page load
        handleResize();
    }
    
    /**
     * Toggle sidebar collapsed/expanded state
     */
    function toggleSidebar() {
        if (!sidebar) return;
        
        const isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
        
        if (isMobile) {
            // Mobile behavior: slide in/out with overlay
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        } else {
            // Desktop behavior: collapse/expand
            sidebar.classList.toggle('collapsed');
            
            // Update main content
            if (mainContent) {
                mainContent.classList.toggle('sidebar-collapsed');
            }
            
            // Save state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem(STORAGE_KEY, isCollapsed);
        }
    }
    
    /**
     * Load sidebar state from localStorage
     */
    function loadSidebarState() {
        const isCollapsed = localStorage.getItem(STORAGE_KEY) === 'true';
        const isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
        
        if (!isMobile && isCollapsed) {
            sidebar.classList.add('collapsed');
            if (mainContent) {
                mainContent.classList.add('sidebar-collapsed');
            }
        }
    }
    
    /**
     * Add tooltip attributes to sidebar items
     */
    function addTooltips() {
        const sidebarItems = document.querySelectorAll('.sidebar-item');
        
        sidebarItems.forEach(item => {
            const text = item.querySelector('.sidebar-text');
            if (text) {
                item.setAttribute('data-tooltip', text.textContent.trim());
            }
        });
    }
    
    /**
     * Handle window resize events
     */
    function handleResize() {
        const isMobile = window.innerWidth <= MOBILE_BREAKPOINT;
        
        if (isMobile) {
            // Remove collapsed state on mobile
            sidebar.classList.remove('collapsed');
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            
            if (mainContent) {
                mainContent.classList.remove('sidebar-collapsed');
            }
        } else {
            // Restore saved state on desktop
            loadSidebarState();
        }
    }
    
    /**
     * Set active navigation item based on current URL
     */
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.sidebar-item');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && href !== '#') {
                // Remove active class
                item.classList.remove('active');
                
                // Check if current path matches
                if (currentPath === href || currentPath.startsWith(href + '/')) {
                    item.classList.add('active');
                }
            }
        });
    }
    
    /**
     * Update sidebar badge counts (can be called from other scripts)
     */
    window.updateSidebarBadge = function(badgeType, count) {
        const badgeMap = {
            'locations': '.sidebar-item[href*="locations"] .sidebar-badge',
            'additional_insureds': '.sidebar-item[href*="additional_insureds"] .sidebar-badge',
            'documents': '.sidebar-item[href*="documents"] .sidebar-badge',
            'endorsements': '.sidebar-item[href*="endorsements"] .sidebar-badge',
            'certificates': '.sidebar-item[href*="certificates"] .sidebar-badge',
            'billing': '.sidebar-item[href*="billing"] .sidebar-badge',
            'claims': '.sidebar-item[href*="claims"] .sidebar-badge'
        };
        
        const badgeElement = document.querySelector(badgeMap[badgeType]);
        if (badgeElement) {
            badgeElement.textContent = count;
            badgeElement.style.display = count > 0 ? 'inline-block' : 'none';
        }
    };
    
    /**
     * Programmatically collapse sidebar
     */
    window.collapseSidebar = function() {
        if (sidebar && !sidebar.classList.contains('collapsed')) {
            toggleSidebar();
        }
    };
    
    /**
     * Programmatically expand sidebar
     */
    window.expandSidebar = function() {
        if (sidebar && sidebar.classList.contains('collapsed')) {
            toggleSidebar();
        }
    };
    
    /**
     * Check if sidebar is collapsed
     */
    window.isSidebarCollapsed = function() {
        return sidebar && sidebar.classList.contains('collapsed');
    };
    
    // Make toggleSidebar globally available
    window.toggleSidebar = toggleSidebar;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initSidebar();
            setActiveNavItem();
        });
    } else {
        initSidebar();
        setActiveNavItem();
    }
    
})();