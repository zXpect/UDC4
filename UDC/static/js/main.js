// Script principal para la aplicación NetSchool con animaciones mejoradas
document.addEventListener('DOMContentLoaded', function() {
    console.log('NetSchool - Sistema de Gestión de Contenidos cargado correctamente (main.js)');
    
    // ========================================
    // INICIALIZACIÓN DE COMPONENTES
    // ========================================
    
    // Inicializar tooltips de Bootstrap si existen
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ========================================
    // GESTIÓN DE TEMA OSCURO/CLARO
    // ========================================

    // Verificar si hay una preferencia guardada
    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Aplicar tema guardado o usar preferencia del sistema
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-theme');
    } else if (savedTheme === 'light') {
        document.documentElement.classList.add('light-theme');
    } else if (prefersDarkScheme.matches) {
        document.documentElement.classList.add('dark-theme');
    }
    
    // Actualizar el ícono del botón de tema
    updateThemeToggleIcon();
    
    // Agregar evento al botón de cambio de tema
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        console.log('Evento de cambio de tema registrado');
    } else {
        console.warn('No se encontró el botón de cambio de tema (.theme-toggle)');
    }
    
    function toggleTheme() {
        console.log('Cambiando tema...');
        if (document.documentElement.classList.contains('dark-theme')) {
            document.documentElement.classList.remove('dark-theme');
            document.documentElement.classList.add('light-theme');
            localStorage.setItem('theme', 'light');
            console.log('Tema cambiado a claro');
        } else {
            document.documentElement.classList.remove('light-theme');
            document.documentElement.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
            console.log('Tema cambiado a oscuro');
        }
        
        updateThemeToggleIcon();
    }
    
    function updateThemeToggleIcon() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) return;
        
        const sunIcon = themeToggle.querySelector('.fa-sun');
        const moonIcon = themeToggle.querySelector('.fa-moon');
        
        if (!sunIcon || !moonIcon) {
            console.warn('No se encontraron los iconos del sol o la luna en el botón de tema');
            return;
        }
        
        if (document.documentElement.classList.contains('dark-theme')) {
            sunIcon.style.opacity = '1';
            sunIcon.style.transform = 'translateY(0) rotate(0)';
            moonIcon.style.opacity = '0';
            moonIcon.style.transform = 'translateY(-20px) rotate(-90deg)';
        } else {
            sunIcon.style.opacity = '0';
            sunIcon.style.transform = 'translateY(20px) rotate(90deg)';
            moonIcon.style.opacity = '1';
            moonIcon.style.transform = 'translateY(0) rotate(0)';
        }
    }

    // ========================================
    // NAVEGACIÓN Y NAVBAR
    // ========================================
    
    const navbar = document.querySelector('.navbar');
    
    // Animación del navbar al hacer scroll
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-lg');
                navbar.style.padding = '0.5rem 1rem';
                navbar.style.background = 'var(--glass)';
                navbar.style.backdropFilter = 'blur(10px)';
            } else {
                navbar.classList.remove('shadow-lg');
                navbar.style.padding = '1rem';
                navbar.style.background = '';
                navbar.style.backdropFilter = '';
            }
        });
    }
    
    // Manejo del menú móvil
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbarNav');
    
    if (navbarToggler && navbarCollapse) {
        // Event listener for when the collapse element is shown
        navbarCollapse.addEventListener('show.bs.collapse', function () {
            document.body.style.overflow = 'hidden'; // Prevent scrolling
            // Optional: Change toggler icon to 'X' if you have a specific class or structure for it
            // Example: navbarToggler.querySelector('.toggler-icon').classList.add('is-active');
        });

        // Event listener for when the collapse element is hidden
        navbarCollapse.addEventListener('hide.bs.collapse', function () {
            document.body.style.overflow = ''; // Restore scrolling
            // Optional: Change toggler icon back to burger
            // Example: navbarToggler.querySelector('.toggler-icon').classList.remove('is-active');
        });

        // Cerrar menú al hacer clic en enlaces dentro del menú desplegable
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                const collapseInstance = bootstrap.Collapse.getInstance(navbarCollapse);
                if (collapseInstance && navbarCollapse.classList.contains('show')) {
                    collapseInstance.hide();
                }
            });
        });

        // Cerrar menú al presionar Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navbarCollapse.classList.contains('show')) {
                const collapseInstance = bootstrap.Collapse.getInstance(navbarCollapse);
                if (collapseInstance) {
                    collapseInstance.hide();
                }
            }
        });
    } else {
        if (!navbarToggler) console.warn('Navbar toggler (.navbar-toggler) not found.');
        if (!navbarCollapse) console.warn('Navbar collapse element (#navbarNav) not found.');
    }

    // Manejar estado activo de los enlaces
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath ||
            (currentPath === '/' && link.getAttribute('href').includes('index'))) {
            link.classList.add('active');
        }
    });

    // ========================================
    // DROPDOWNS MEJORADOS
    // ========================================
    
    // Mejorar dropdowns en móviles
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        if (dropdownToggle && dropdownMenu) {
            // En móviles, evitar que el menú se salga de la pantalla
            if (window.innerWidth < 992) {
                dropdownMenu.style.position = 'static';
                dropdownMenu.style.width = '100%';
                dropdownMenu.style.margin = '0.5rem 0';
                dropdownMenu.style.boxShadow = 'none';
            }
            
            // Añadir clase para animación
            dropdownMenu.classList.add('dropdown-animation');
            
            // Mejorar interacción en móviles
            if ('ontouchstart' in window) {
                dropdownToggle.addEventListener('click', function(e) {
                    if (window.innerWidth < 992) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        dropdownMenu.classList.toggle('show');
                        
                        // Cerrar otros dropdowns
                        dropdowns.forEach(otherDropdown => {
                            if (otherDropdown !== dropdown) {
                                const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                                if (otherMenu && otherMenu.classList.contains('show')) {
                                    otherMenu.classList.remove('show');
                                }
                            }
                        });
                    }
                });
            }
        }
    });

    // ========================================
    // ANIMACIONES DE SCROLL
    // ========================================
    
    // Animación para cards cuando están visibles
    const animateOnScroll = function() {
        const cards = document.querySelectorAll('.card, .service-card');
        cards.forEach(card => {
            const cardPosition = card.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (cardPosition < screenPosition) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }
        });
    };

    // Inicialmente ocultar las cards para animarlas cuando sean visibles
    document.querySelectorAll('.card, .service-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
    });

    // Detectar cuando se hace scroll para animar elementos
    window.addEventListener('scroll', animateOnScroll);
    // Ejecutar una vez al cargar la página
    animateOnScroll();

    // ========================================
    // EFECTOS INTERACTIVOS
    // ========================================
    
    // Añadir efecto hover para los iconos en los servicios
    const serviceIcons = document.querySelectorAll('.service-icon i, .card i.fas, .card i.far, .card i.fab');
    serviceIcons.forEach(icon => {
        icon.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.2) rotate(5deg)';
            this.style.transition = 'all 0.3s ease';
        });
        
        icon.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1) rotate(0)';
        });
    });

    // Animación para botones
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            if (!this.disabled) {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                this.style.transition = 'all 0.3s ease';
            }
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });

    // Efecto de enfoque para el formulario de contacto
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#3b82f6';
            this.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.25)';
            this.style.transition = 'all 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    });

    // ========================================
    // EFECTOS DE RIPPLE
    // ========================================
    
    // Añadir efecto de ripple a botones y enlaces
    function createRipple(event) {
        const button = event.currentTarget;
        
        // Verificar si el elemento ya tiene posición relativa
        const buttonPosition = window.getComputedStyle(button).getPropertyValue('position');
        if (buttonPosition !== 'relative' && buttonPosition !== 'absolute') {
            button.style.position = 'relative';
        }
        
        // Verificar si el elemento ya tiene overflow hidden
        const buttonOverflow = window.getComputedStyle(button).getPropertyValue('overflow');
        if (buttonOverflow !== 'hidden') {
            button.style.overflow = 'hidden';
        }
        
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        const rect = button.getBoundingClientRect();
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.classList.add('ripple');
        
        const ripple = button.getElementsByClassName('ripple')[0];
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
        
        // Remover después de la animación
        setTimeout(() => {
            if (circle.parentElement) {
                circle.remove();
            }
        }, 600);
    }
    
    // Aplicar efecto ripple a botones y enlaces
    const rippleElements = document.querySelectorAll('.btn, .service-link, .nav-link, .dropdown-item');
    rippleElements.forEach(element => {
        element.addEventListener('click', createRipple);
    });
    
    // Añadir CSS para el efecto de ripple
    if (!document.getElementById('ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 600ms linear;
                background-color: rgba(255, 255, 255, 0.3);
                pointer-events: none;
                z-index: 10;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            /* Overlay para menú móvil */
            .navbar-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 1040;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .navbar-overlay.active {
                opacity: 1;
                visibility: visible;
            }
            
            /* Animación para dropdown */
            .dropdown-animation {
                animation: fadeInDown 0.3s ease;
            }
            
            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Navbar móvil */
            @media (max-width: 991px) {
                .navbar-collapse {
                    position: fixed;
                    top: 0;
                    right: -280px;
                    width: 280px;
                    height: 100vh;
                    background: var(--glass);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border-left: 1px solid var(--border);
                    padding: 1rem;
                    transition: right 0.3s ease;
                    z-index: 1050;
                    overflow-y: auto;
                }
                
                .navbar-collapse.show {
                    right: 0;
                }
                
                .navbar-nav {
                    margin-top: 3rem;
                }
                
                .nav-item {
                    margin-bottom: 0.5rem;
                }
                
                .dropdown-menu {
                    background: var(--surface) !important;
                    border: 1px solid var(--border) !important;
                }
            }

            /* Corrección de color para form-control-plaintext en tema oscuro */
            .dark-theme .form-control-plaintext {
                color:rgb(190, 190, 190); /* Color de texto blanco puro */
            }
            .dark-theme .form-label {
                color:rgb(255, 255, 255); /* Color de texto blanco puro para las etiquetas */
            }
        `;
        document.head.appendChild(style);
    }

    // ========================================
    // ALERTAS Y NOTIFICACIONES
    // ========================================
    
    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                alert.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
        
        // Añadir funcionalidad al botón de cerrar
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                alert.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    alert.remove();
                }, 500);
            });
        }
    });

    // ========================================
    // DASHBOARD SPECIFIC LOGIC
    // ========================================
    // Solo ejecutar si estamos en una página con elementos del dashboard
    const adminDashboardSpecificElementsPresent = document.getElementById('editEventModal') || 
                                              document.querySelector('.edit-event-btn') || 
                                              document.getElementById('addEventModal'); // Añadir otros selectores relevantes si es necesario

    if (adminDashboardSpecificElementsPresent) {
        console.log('CONSOLE LOG (from main.js): Dashboard-specific elements detected. Initializing dashboard event listeners.');

        // Edit Event Modal Trigger Logic
        document.querySelectorAll('.edit-event-btn').forEach(button => {
            console.log('CONSOLE LOG (from main.js): Attaching click listener to an .edit-event-btn', button);
            button.addEventListener('click', function() {
                console.log('CONSOLE LOG (from main.js): .edit-event-btn clicked.', this);
                const eventId = this.getAttribute('data-event-id');
                console.log('CONSOLE LOG (from main.js): Retrieved data-event-id:', eventId);
                if (!eventId) {
                    console.error('ERROR (JS from main.js): data-event-id attribute not found or empty on edit button.');
                    alert('Error en el cliente (JS): No se pudo obtener el ID del evento desde el botón.');
                    return;
                }
                // Llama a la función setupEditModal (que está ahora en este mismo archivo main.js)
                setupEditModal(eventId, this); 
            });
        });

        const editForm = document.getElementById('editEventForm');
        if (editForm) {
            console.log('CONSOLE LOG (from main.js): Attaching submit listener to #editEventForm.');
            editForm.addEventListener('submit', function(e) {
                console.log('CONSOLE LOG (from main.js): Submit event triggered for #editEventForm.');
                
                const idFieldElement = document.getElementById('editEventId');
                const idFromDom = idFieldElement ? idFieldElement.value : 'DOM ELEMENT NOT FOUND';
                console.log('CONSOLE LOG (from main.js): Value of #editEventId from DOM at submit time:', idFromDom);

                const formData = new FormData(this);
                console.log('CONSOLE LOG (from main.js): Form data captured for #editEventForm:');
                for (let [key, value] of formData.entries()) {
                    console.log(`CONSOLE LOG (from main.js): FormData entry - ${key}: ${value}`);
                }
                
                const eventIdFromFormData = formData.get('eventId');
                console.log('CONSOLE LOG (from main.js): eventId extracted from FormData for #editEventForm:', eventIdFromFormData);

                if (!eventIdFromFormData || eventIdFromFormData.trim() === '') {
                    console.error('ERROR (JS from main.js): eventId is missing or empty from #editEventForm data! Submission blocked.');
                    alert('Error en el cliente (JS): El ID del evento está ausente o vacío. No se puede enviar.');
                    e.preventDefault();
                    return false; 
                }
                
                console.log('CONSOLE LOG (from main.js): Form validation passed for #editEventForm. eventId to be submitted:', eventIdFromFormData, '. Allowing native form submission to proceed.');
            });
        } else {
            console.log('CONSOLE LOG (from main.js): #editEventForm not found. Submit listener not attached.');
        }

        // View Event Details Logic
        document.querySelectorAll('.view-event-btn').forEach(button => {
            console.log('CONSOLE LOG (from main.js): Attaching click listener to a .view-event-btn', button);
            button.addEventListener('click', function() {
                console.log('CONSOLE LOG (from main.js): .view-event-btn clicked', this);
                const title = this.getAttribute('data-event-title');
                const date = this.getAttribute('data-event-date');
                const time = this.getAttribute('data-event-time');
                const location = this.getAttribute('data-event-location');
                const description = this.getAttribute('data-event-description');
                
                const viewEventTitle = document.getElementById('viewEventTitle');
                const viewEventDate = document.getElementById('viewEventDate');
                const viewEventTime = document.getElementById('viewEventTime');
                const viewEventLocation = document.getElementById('viewEventLocation');
                const viewEventDescription = document.getElementById('viewEventDescription');

                if (viewEventTitle) viewEventTitle.textContent = title || '';
                if (viewEventDate) viewEventDate.textContent = date || '';
                if (viewEventTime) viewEventTime.textContent = time || '';
                if (viewEventLocation) viewEventLocation.textContent = location || '';
                if (viewEventDescription) viewEventDescription.textContent = description || '';
                
                const viewEventModalElement = document.getElementById('viewEventModal');
                if (viewEventModalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    new bootstrap.Modal(viewEventModalElement).show();
                } else {
                     console.error('ERROR (JS from main.js): #viewEventModal or Bootstrap Modal not found for .view-event-btn.');
                }
            });
        });
        
        const editEventModalElement = document.getElementById('editEventModal');
        if (editEventModalElement) {
            console.log('CONSOLE LOG (from main.js): Attaching shown.bs.modal listener to #editEventModal.');
            editEventModalElement.addEventListener('shown.bs.modal', function () {
                const eventIdFromField = document.getElementById('editEventId') ? document.getElementById('editEventId').value : 'ID FIELD NOT FOUND';
                console.log('CONSOLE LOG (from main.js): #editEventModal shown, current event ID in field (#editEventId):', eventIdFromField);
            });
        } else {
            console.log('CONSOLE LOG (from main.js): #editEventModal not found. shown.bs.modal listener not attached.');
        }


    } else {
        console.log('CONSOLE LOG (from main.js): Dashboard-specific elements not detected. Skipping dashboard event listeners initialization.');
    }
    
    console.log('NetSchool - Todas las funcionalidades cargadas correctamente (main.js DOMContentLoaded end)');

    // Simple dropdown animation
    const userMenuToggle = document.querySelector('.user-menu-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (userMenuToggle && dropdownMenu) {
        userMenuToggle.addEventListener('click', function() {
            dropdownMenu.style.animation = 'dropdownSlide 0.3s ease';
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.querySelector('.dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                dropdownMenu.classList.remove('show');
            }
        }
    });
});

// ========================================
// FUNCIONES GLOBALES
// ========================================

// Función para mostrar notificaciones
window.showNotification = function(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = `
        <div class="alert-content">
            <div class="alert-title">${type === 'success' ? '¡Éxito!' : type === 'error' ? 'Error!' : 'Información'}</div>
            <p>${message}</p>
        </div>
        <button type="button" class="alert-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Estilos para la notificación
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    notification.style.transition = 'all 0.3s ease';
    
    document.body.appendChild(notification);
    
    // Mostrar notificación
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Cerrar notificación
    const closeBtn = notification.querySelector('.alert-close');
    closeBtn.addEventListener('click', () => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto-cerrar
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
};

// Función para cargar contenido dinámicamente
window.loadContent = function(url, container) {
    const containerEl = typeof container === 'string' ? document.querySelector(container) : container;
    if (!containerEl) return;
    
    containerEl.classList.add('loading');
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            containerEl.innerHTML = html;
            containerEl.classList.remove('loading');
            
            // Re-inicializar componentes en el nuevo contenido
            const event = new CustomEvent('contentLoaded', { detail: { container: containerEl } });
            document.dispatchEvent(event);
        })
        .catch(error => {
            console.error('Error loading content:', error);
            showNotification('Error al cargar el contenido', 'error');
        });
};

// Moved from dashboard.html - Needs to be accessible to listeners
function setupEditModal(eventId, button) {
    console.log('CONSOLE LOG (from main.js): setupEditModal called with ID:', eventId);
    
    const idField = document.getElementById('editEventId');
    if (idField) {
        idField.value = eventId;
        console.log('CONSOLE LOG (from main.js): Event ID field (#editEventId) set to:', idField.value);
    } else {
        console.error('ERROR (JS from main.js): Could not find #editEventId field in setupEditModal!');
    }
    
    const title = button.getAttribute('data-event-title') || '';
    const date = button.getAttribute('data-event-date') || '';
    const time = button.getAttribute('data-event-time') || '';
    const location = button.getAttribute('data-event-location') || '';
    const description = button.getAttribute('data-event-description') || '';

    const titleField = document.getElementById('editEventTitle');
    const dateField = document.getElementById('editEventDate');
    const timeField = document.getElementById('editEventTime');
    const locationField = document.getElementById('editEventLocation');
    const descriptionField = document.getElementById('editEventDescription');

    if (titleField) titleField.value = title;
    if (dateField) dateField.value = date;
    if (timeField) timeField.value = time;
    if (locationField) locationField.value = location;
    if (descriptionField) descriptionField.value = description;

    console.log('CONSOLE LOG (from main.js): Form fields in setupEditModal after filling:', {
        id: idField ? idField.value : 'ID FIELD NOT FOUND',
        title: titleField ? titleField.value : 'TITLE FIELD NOT FOUND',
        date: dateField ? dateField.value : 'DATE FIELD NOT FOUND',
        time: timeField ? timeField.value : 'TIME FIELD NOT FOUND',
        location: locationField ? locationField.value : 'LOCATION FIELD NOT FOUND',
        description: descriptionField ? descriptionField.value : 'DESCRIPTION FIELD NOT FOUND'
    });
}


