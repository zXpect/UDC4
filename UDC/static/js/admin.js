/**
 * NetSchool UDC - Admin Dashboard JavaScript
 * Optimized for perfect dashboard functionality
 */

class AdminDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initSidebar();
        this.initNotifications();
        this.initTasks();
        this.initTooltips();
        this.initThemeToggle();
        this.initSearch();
        this.initModals();
        this.initCharts();
        this.initEventHandlers();
    }

    // Sidebar functionality
    initSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
        const adminContainer = document.querySelector('.admin-container');
        
        // Mobile sidebar toggle
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.body.classList.toggle('sidebar-mobile-open');
            });
        }

        // Desktop sidebar collapse
        if (sidebarCollapseBtn) {
            sidebarCollapseBtn.addEventListener('click', () => {
                adminContainer.classList.toggle('sidebar-collapsed');
                
                // Save collapse state
                localStorage.setItem('sidebarCollapsed', 
                    adminContainer.classList.contains('sidebar-collapsed')
                );
                
                // Trigger resize event for charts
                setTimeout(() => {
                    window.dispatchEvent(new Event('resize'));
                }, 300);
            });
        }

        // Restore sidebar state
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed && adminContainer) {
            adminContainer.classList.add('sidebar-collapsed');
        }

        // Close mobile sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                !e.target.closest('.admin-sidebar') && 
                !e.target.closest('#sidebarToggle')) {
                document.body.classList.remove('sidebar-mobile-open');
            }
        });

        // Handle nav item active states
        this.initNavigation();
    }

    initNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href === currentPath) {
                link.closest('.nav-item').classList.add('active');
            }
            
            link.addEventListener('click', (e) => {
                // Don't prevent default for actual links
                if (href && href !== '#') return;
                
                e.preventDefault();
                
                // Remove active from all items
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active to clicked item
                link.closest('.nav-item').classList.add('active');
            });
        });
    }

    // Notifications system
    initNotifications() {
        const notificationBtn = document.querySelector('.notification-btn');
        const notificationItems = document.querySelectorAll('.notification-item');
        const markAllReadBtn = document.querySelector('.dropdown-header a');
        
        // Handle individual notification clicks
        notificationItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                if (item.classList.contains('unread')) {
                    item.classList.remove('unread');
                    this.updateNotificationCount(-1);
                }
            });
        });

        // Mark all notifications as read
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                
                const unreadCount = document.querySelectorAll('.notification-item.unread').length;
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                });
                
                this.updateNotificationCount(-unreadCount);
            });
        }
    }

    updateNotificationCount(change) {
        const badge = document.querySelector('.notification-btn .badge');
        if (!badge) return;
        
        const currentCount = parseInt(badge.textContent) || 0;
        const newCount = Math.max(0, currentCount + change);
        
        if (newCount > 0) {
            badge.textContent = newCount;
            badge.style.display = 'inline-block';
        } else {
            badge.textContent = '';
            badge.style.display = 'none';
        }
    }

    // Task management
    initTasks() {
        const taskCheckboxes = document.querySelectorAll('.task-item .form-check-input');
        
        taskCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const taskItem = this.closest('.task-item');
                const label = taskItem.querySelector('.form-check-label');
                
                if (this.checked) {
                    taskItem.classList.add('completed');
                    label.style.textDecoration = 'line-through';
                    label.style.opacity = '0.6';
                    
                    // Add completion animation
                    taskItem.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        taskItem.style.transform = 'scale(1)';
                    }, 150);
                } else {
                    taskItem.classList.remove('completed');
                    label.style.textDecoration = 'none';
                    label.style.opacity = '1';
                }
            });
        });
    }

    // Initialize tooltips
    initTooltips() {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(
                document.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            tooltipTriggerList.map(tooltipTriggerEl => 
                new bootstrap.Tooltip(tooltipTriggerEl)
            );
        }
    }

    // Theme toggle functionality
    initThemeToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Load saved theme or use system preference
        const savedTheme = localStorage.getItem('theme') || 
                          (prefersDark.matches ? 'dark' : 'light');
        
        this.setTheme(savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
            });
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            const sunIcon = themeToggle.querySelector('.fa-sun');
            const moonIcon = themeToggle.querySelector('.fa-moon');
            
            if (theme === 'dark') {
                sunIcon.style.display = 'inline-block';
                moonIcon.style.display = 'none';
            } else {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'inline-block';
            }
        }
    }

    // Search functionality
    initSearch() {
        const searchInput = document.querySelector('.search-box input');
        
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                
                searchTimeout = setTimeout(() => {
                    const query = e.target.value.toLowerCase().trim();
                    this.performSearch(query);
                }, 300);
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const query = e.target.value.toLowerCase().trim();
                    this.performSearch(query);
                }
            });
        }
    }

    performSearch(query) {
        if (!query) return;
        
        // Simple search implementation - can be extended
        const searchableElements = document.querySelectorAll(
            '.nav-link span, .card-title, .event-item span, .task-item label'
        );
        
        searchableElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            const container = element.closest('.nav-item, .card, tr, .task-item');
            
            if (container) {
                if (text.includes(query)) {
                    container.style.display = '';
                    element.style.backgroundColor = '#fff3cd';
                } else {
                    container.style.display = 'none';
                    element.style.backgroundColor = '';
                }
            }
        });
        
        // Clear highlights after 3 seconds
        setTimeout(() => {
            searchableElements.forEach(element => {
                element.style.backgroundColor = '';
                element.closest('.nav-item, .card, tr, .task-item').style.display = '';
            });
        }, 3000);
    }

    // Modal functionality
    initModals() {
        const addEventForm = document.getElementById('addEventForm');
        
        if (addEventForm) {
            addEventForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddEvent();
            });
        }

        // Save button for add event modal
        const saveEventBtn = document.querySelector('#addEventModal .btn-primary');
        if (saveEventBtn) {
            saveEventBtn.addEventListener('click', () => {
                this.handleAddEvent();
            });
        }
    }

    handleAddEvent() {
        const form = document.getElementById('addEventForm');
        const formData = new FormData(form);
        
        // Basic validation
        const title = document.getElementById('eventTitle').value.trim();
        const date = document.getElementById('eventDate').value;
        const status = document.getElementById('eventStatus').value;
        
        if (!title || !date || !status) {
            alert('Por favor, complete todos los campos requeridos.');
            return;
        }
        
        // Here you would typically send data to server
        console.log('Adding event:', {
            title,
            date,
            status,
            location: document.getElementById('eventLocation').value,
            time: document.getElementById('eventTime').value,
            description: document.getElementById('eventDescription').value
        });
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('addEventModal'));
        if (modal) {
            modal.hide();
        }
        form.reset();
        
        // Show success message
        this.showToast('Evento agregado exitosamente', 'success');
    }

    // Initialize charts
    initCharts() {
        // Only initialize if Chart.js is available
        if (typeof Chart === 'undefined') return;
        
        this.initUserStatsChart();
        this.initUserDistributionChart();
    }

    initUserStatsChart() {
        const ctx = document.getElementById('userStatsChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                datasets: [
                    {
                        label: 'Estudiantes',
                        data: [65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Profesores',
                        data: [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initUserDistributionChart() {
        const ctx = document.getElementById('userDistributionChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Estudiantes', 'Profesores', 'Administradores'],
                datasets: [{
                    data: [120, 26, 7],
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            boxWidth: 12
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Additional event handlers
    initEventHandlers() {
        // Table action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.classList.contains('edit') ? 'edit' :
                              btn.classList.contains('delete') ? 'delete' : 'view';
                
                console.log(`Action: ${action}`);
                // Handle specific actions here
            });
        });

        // Quick access items
        document.querySelectorAll('.quick-access-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                item.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    item.style.transform = 'scale(1)';
                }, 150);
            });
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                document.body.classList.remove('sidebar-mobile-open');
            }
        });
    }

    // Utility function for toast notifications
    showToast(message, type = 'info') {
        // Create toast element if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback without Bootstrap
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AdminDashboard();
});

// Export for use in other scripts if needed
window.AdminDashboard = AdminDashboard;

