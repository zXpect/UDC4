// Script principal para la aplicación NetSchool con animaciones mejoradas
document.addEventListener('DOMContentLoaded', function() {
    console.log('NetSchool - Sistema de Gestión de Contenidos cargado correctamente');
    
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
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Crear overlay para cerrar menú
        const navbarOverlay = document.createElement('div');
        navbarOverlay.className = 'navbar-overlay';
        document.body.appendChild(navbarOverlay);
        
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
            
            if (navbarCollapse.classList.contains('show')) {
                navbarOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                navbarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Cerrar menú al hacer clic en overlay
        navbarOverlay.addEventListener('click', function() {
            navbarCollapse.classList.remove('show');
            navbarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Cerrar menú al hacer clic en enlaces
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                    navbarOverlay.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        });
    }

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
    
    console.log('NetSchool - Todas las funcionalidades cargadas correctamente');
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

