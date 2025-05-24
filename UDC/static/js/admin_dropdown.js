// JavaScript consolidado para admin dashboard
document.addEventListener('DOMContentLoaded', function() {
    
    console.log('Admin dashboard JavaScript cargado');
    
    // ========================================
    // ELEMENTOS DEL DOM
    // ========================================
    
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminContainer = document.querySelector('.admin-container');
    const adminSidebar = document.querySelector('.admin-sidebar');
    
    console.log('Elementos encontrados:', {
        sidebarCollapseBtn: !!sidebarCollapseBtn,
        sidebarToggle: !!sidebarToggle,
        adminContainer: !!adminContainer,
        adminSidebar: !!adminSidebar
    });

    // ========================================
    // FUNCIONALIDAD SIDEBAR COLLAPSE (Desktop)
    // ========================================
    
    if (sidebarCollapseBtn && adminContainer) {
        sidebarCollapseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Botón collapse clickeado');
            
            // Toggle clase
            adminContainer.classList.toggle('sidebar-collapsed');
            
            const isCollapsed = adminContainer.classList.contains('sidebar-collapsed');
            console.log('Sidebar collapsed:', isCollapsed);
            
            // Guardar estado en localStorage
            localStorage.setItem('sidebarCollapsed', isCollapsed.toString());
            
            // Trigger resize event para gráficos
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 300);
        });
    } else {
        console.warn('No se encontró el botón de collapse o el container');
    }

    // ========================================
    // FUNCIONALIDAD SIDEBAR MOBILE
    // ========================================
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Toggle mobile clickeado');
            document.body.classList.toggle('sidebar-mobile-open');
        });
    }

    // ========================================
    // RESTAURAR ESTADO DEL SIDEBAR
    // ========================================
    
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true' && adminContainer) {
        adminContainer.classList.add('sidebar-collapsed');
        console.log('Estado del sidebar restaurado: collapsed');
    }

    // ========================================
    // CERRAR SIDEBAR MOBILE AL CLICK FUERA
    // ========================================
    
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.admin-sidebar') && 
                !e.target.closest('#sidebarToggle')) {
                document.body.classList.remove('sidebar-mobile-open');
            }
        }
    });

    // ========================================
    // MANEJAR RESIZE DE VENTANA
    // ========================================
    
    window.addEventListener('resize', function() {
        // Si cambiamos a desktop, remover clase mobile
        if (window.innerWidth > 768) {
            document.body.classList.remove('sidebar-mobile-open');
        }
    });

    // ========================================
    // DROPDOWNS DEL HEADER
    // ========================================
    
    const adminDropdowns = document.querySelectorAll('.admin-header .dropdown');
    
    adminDropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Cerrar otros dropdowns
                adminDropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                        if (otherMenu) {
                            otherMenu.classList.remove('show');
                        }
                    }
                });
                
                // Toggle dropdown actual
                menu.classList.toggle('show');
            });
        }
    });
    
    // Cerrar dropdowns al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.admin-header .dropdown')) {
            adminDropdowns.forEach(dropdown => {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.remove('show');
                }
            });
        }
    });
    
    // Cerrar dropdowns con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            adminDropdowns.forEach(dropdown => {
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) {
                    menu.classList.remove('show');
                }
            });
        }
    });

    // ========================================
    // INICIALIZAR TOOLTIPS
    // ========================================
    
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipElements.forEach(element => {
            new bootstrap.Tooltip(element);
        });
    }

    // ========================================
    // CHECKBOXES DE TAREAS
    // ========================================
    
    const taskCheckboxes = document.querySelectorAll('.task-item .form-check-input');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskItem = this.closest('.task-item');
            if (this.checked) {
                taskItem.classList.add('completed');
            } else {
                taskItem.classList.remove('completed');
            }
        });
    });

    // ========================================
    // FORMULARIO DE EVENTOS
    // ========================================
    
    const addEventForm = document.getElementById('addEventForm');
    const addEventModal = document.getElementById('addEventModal');
    
    if (addEventForm && addEventModal) {
        const modalInstance = new bootstrap.Modal(addEventModal);
        
        addEventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(addEventForm);
            
            // Aquí iría tu lógica de AJAX para enviar el formulario
            console.log('Formulario de evento enviado');
            
            modalInstance.hide();
            showAlert('success', 'Evento creado exitosamente');
        });
    }

    // ========================================
    // FUNCIÓN PARA MOSTRAR ALERTAS
    // ========================================
    
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.admin-content');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        }

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // Hacer función disponible globalmente
    window.showAlert = showAlert;
});