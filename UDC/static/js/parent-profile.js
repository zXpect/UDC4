class ParentProfile {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Filtros de calificaciones
        document.getElementById('child-filter')?.addEventListener('change', this.handleGradeFilters.bind(this));
        document.getElementById('period-filter')?.addEventListener('change', this.handleGradeFilters.bind(this));
        
        // Filtros de asistencia
        document.getElementById('attendance-child-filter')?.addEventListener('change', this.handleAttendanceFilters.bind(this));
        document.getElementById('attendance-month-filter')?.addEventListener('change', this.handleAttendanceFilters.bind(this));
        
        // Manejo de mensajes
        document.getElementById('send-message')?.addEventListener('click', this.handleSendMessage.bind(this));
        
        // Manejo de pestañas
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => this.switchTab(item.dataset.tab));
        });
    }

    async handleGradeFilters() {
        const childId = document.getElementById('child-filter')?.value;
        const periodId = document.getElementById('period-filter')?.value;
        
        try {
            const response = await fetch(`/api/parent/grades?child_id=${childId}&period_id=${periodId}`);
            if (!response.ok) throw new Error('Error al filtrar las calificaciones');

            const data = await response.json();
            this.updateGradesTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async handleAttendanceFilters() {
        const childId = document.getElementById('attendance-child-filter')?.value;
        const month = document.getElementById('attendance-month-filter')?.value;
        
        try {
            const response = await fetch(`/api/parent/attendance?child_id=${childId}&month=${month}`);
            if (!response.ok) throw new Error('Error al filtrar la asistencia');

            const data = await response.json();
            this.updateAttendanceTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async handleSendMessage(e) {
        e.preventDefault();
        const form = document.getElementById('new-message-form');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/parent/messages', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al enviar el mensaje');

            const data = await response.json();
            this.addMessageToUI(data);
            this.showToast('Mensaje enviado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('new-message-modal')).hide();
            form.reset();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    switchTab(tabId) {
        // Ocultar todas las pestañas
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Mostrar la pestaña seleccionada
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) {
            selectedTab.style.display = 'block';
        }
        
        // Actualizar clases activas
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.tab === tabId) {
                item.classList.add('active');
            }
        });

        // Actualizar datos si es necesario
        this.loadTabData(tabId);
    }

    async loadTabData(tabId) {
        switch (tabId) {
            case 'children':
                await this.loadChildren();
                break;
            case 'grades':
                await this.loadGrades();
                break;
            case 'attendance':
                await this.loadAttendance();
                break;
            case 'messages':
                await this.loadMessages();
                break;
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadChildren(),
            this.loadGrades(),
            this.loadAttendance(),
            this.loadMessages()
        ]);
    }

    async loadChildren() {
        try {
            const response = await fetch('/api/parent/children');
            if (!response.ok) throw new Error('Error al cargar los hijos');

            const data = await response.json();
            this.updateChildrenUI(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async loadGrades() {
        try {
            const response = await fetch('/api/parent/grades');
            if (!response.ok) throw new Error('Error al cargar las calificaciones');

            const data = await response.json();
            this.updateGradesTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async loadAttendance() {
        try {
            const response = await fetch('/api/parent/attendance');
            if (!response.ok) throw new Error('Error al cargar la asistencia');

            const data = await response.json();
            this.updateAttendanceTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async loadMessages() {
        try {
            const response = await fetch('/api/parent/messages');
            if (!response.ok) throw new Error('Error al cargar los mensajes');

            const data = await response.json();
            this.updateMessagesUI(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    updateChildrenUI(children) {
        const container = document.getElementById('children-container');
        if (!container) return;

        container.innerHTML = children.map(child => this.createChildCard(child)).join('');
    }

    updateGradesTable(grades) {
        const tbody = document.querySelector('#grades-container');
        if (!tbody) return;

        tbody.innerHTML = grades.map(grade => this.createGradeRow(grade)).join('');
    }

    updateAttendanceTable(records) {
        const tbody = document.querySelector('#attendance-container');
        if (!tbody) return;

        tbody.innerHTML = records.map(record => this.createAttendanceRow(record)).join('');
    }

    updateMessagesUI(messages) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        container.innerHTML = messages.map(message => this.createMessageItem(message)).join('');
    }

    createChildCard(child) {
        return `
            <div class="col-md-6 col-xl-4 mb-4">
                <div class="student-card">
                    <div class="student-header">
                        <div class="student-avatar">
                            <img src="${child.avatar_url || '/static/img/default-avatar.png'}" 
                                 alt="Avatar de ${child.first_name}">
                        </div>
                        <div class="student-info">
                            <h6 class="student-name">${child.first_name} ${child.last_name}</h6>
                            <span class="student-id">Matrícula: ${child.student_id}</span>
                        </div>
                    </div>
                    <div class="student-body">
                        <div class="info-item">
                            <span class="info-label">Carrera:</span>
                            <span class="info-value">${child.major}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Semestre:</span>
                            <span class="info-value">${child.semester}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Promedio:</span>
                            <span class="info-value">${child.average_grade}</span>
                        </div>
                    </div>
                    <div class="student-footer">
                        <a href="/parent/children/${child.id}" class="btn btn-primary btn-sm">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </a>
                        <a href="/parent/children/${child.id}/schedule" class="btn btn-info btn-sm">
                            <i class="fas fa-calendar"></i> Ver Horario
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    createGradeRow(grade) {
        return `
            <tr>
                <td>${grade.student_name}</td>
                <td>${grade.course_name}</td>
                <td>${grade.teacher_name}</td>
                <td>${grade.completed_assignments}/${grade.total_assignments}</td>
                <td>${grade.average}</td>
                <td>
                    <span class="badge bg-${grade.average >= 70 ? 'success' : 'danger'}">
                        ${grade.average >= 70 ? 'Aprobado' : 'Reprobado'}
                    </span>
                </td>
            </tr>
        `;
    }

    createAttendanceRow(record) {
        return `
            <tr>
                <td>${record.student_name}</td>
                <td>${record.course_name}</td>
                <td>${record.date}</td>
                <td>
                    <span class="badge bg-${record.status_color}">
                        ${record.status}
                    </span>
                </td>
                <td>${record.notes || '--'}</td>
            </tr>
        `;
    }

    createMessageItem(message) {
        return `
            <div class="message-item">
                <div class="message-header">
                    <div class="message-sender">
                        <img src="${message.sender_avatar || '/static/img/default-avatar.png'}" 
                             alt="Avatar de ${message.sender_name}"
                             class="sender-avatar">
                        <div class="sender-info">
                            <h6 class="sender-name">${message.sender_name}</h6>
                            <span class="sender-role">${message.sender_role}</span>
                        </div>
                    </div>
                    <div class="message-meta">
                        <span class="message-date">${message.date}</span>
                        <span class="message-time">${message.time}</span>
                    </div>
                </div>
                <div class="message-content">
                    <p>${message.content}</p>
                    ${message.attachments ? `
                        <div class="message-attachments">
                            ${message.attachments.map(attachment => `
                                <a href="${attachment.url}" class="attachment-item">
                                    <i class="fas fa-${attachment.icon}"></i>
                                    <span>${attachment.name}</span>
                                </a>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="message-actions">
                    <button class="btn btn-link btn-sm" onclick="parentProfile.replyToMessage('${message.id}')">
                        <i class="fas fa-reply"></i> Responder
                    </button>
                </div>
            </div>
        `;
    }

    addMessageToUI(message) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const messageElement = document.createElement('div');
        messageElement.innerHTML = this.createMessageItem(message);
        container.insertBefore(messageElement.firstChild, container.firstChild);
    }

    async replyToMessage(messageId) {
        // Implementar lógica para responder mensajes
        const modal = document.getElementById('new-message-modal');
        if (!modal) return;

        try {
            const response = await fetch(`/api/parent/messages/${messageId}`);
            if (!response.ok) throw new Error('Error al cargar el mensaje');

            const message = await response.json();
            
            // Pre-llenar el formulario con la información de respuesta
            const form = document.getElementById('new-message-form');
            form.querySelector('[name="recipient_id"]').value = message.sender_id;
            form.querySelector('[name="subject"]').value = `Re: ${message.subject}`;
            
            // Mostrar el modal
            new bootstrap.Modal(modal).show();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    showToast(message, type = 'info') {
        // Usar el sistema de notificaciones global
        if (window.showNotification) {
            window.showNotification(message, type);
        }
    }
}

// Inicializar el perfil del padre
const parentProfile = new ParentProfile(); 