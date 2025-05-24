class TeacherProfile {
    constructor() {
        this.calendar = null;
        this.init();
    }

    init() {
        this.setupCalendar();
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupCalendar() {
        const calendarEl = document.getElementById('schedule-calendar');
        if (!calendarEl) return;

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay'
            },
            slotMinTime: '07:00:00',
            slotMaxTime: '19:00:00',
            allDaySlot: false,
            locale: 'es',
            events: '/api/teacher/schedule',
            eventClick: this.handleEventClick.bind(this),
            eventDidMount: (info) => {
                tippy(info.el, {
                    content: `
                        <strong>${info.event.title}</strong><br>
                        Curso: ${info.event.extendedProps.course}<br>
                        Aula: ${info.event.extendedProps.room}<br>
                        Estudiantes: ${info.event.extendedProps.students}
                    `,
                    allowHTML: true,
                });
            }
        });

        this.calendar.render();
    }

    setupEventListeners() {
        // Manejo de cursos
        document.getElementById('save-course')?.addEventListener('click', this.handleAddCourse.bind(this));
        
        // Manejo de tareas
        document.getElementById('save-assignment')?.addEventListener('click', this.handleAddAssignment.bind(this));
        
        // Filtros de calificaciones
        document.getElementById('course-filter')?.addEventListener('change', this.handleCourseFilter.bind(this));
        
        // Manejo de pestañas
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => this.switchTab(item.dataset.tab));
        });
    }

    async handleAddCourse(e) {
        e.preventDefault();
        const form = document.getElementById('add-course-form');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/teacher/courses', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al crear el curso');

            const data = await response.json();
            this.addCourseToUI(data);
            this.showToast('Curso creado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('add-course-modal')).hide();
            form.reset();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async handleAddAssignment(e) {
        e.preventDefault();
        const form = document.getElementById('add-assignment-form');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/teacher/assignments', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al crear la tarea');

            const data = await response.json();
            this.addAssignmentToUI(data);
            this.showToast('Tarea creada exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('add-assignment-modal')).hide();
            form.reset();
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async handleCourseFilter(e) {
        const courseId = e.target.value;
        try {
            const response = await fetch(`/api/teacher/grades?course_id=${courseId}`);
            if (!response.ok) throw new Error('Error al cargar las calificaciones');

            const data = await response.json();
            this.updateGradesTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    handleEventClick(info) {
        // Implementar lógica para mostrar detalles de la clase
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
            case 'courses':
                await this.loadCourses();
                break;
            case 'assignments':
                await this.loadAssignments();
                break;
            case 'grades':
                await this.loadGrades();
                break;
            case 'schedule':
                this.calendar?.refetchEvents();
                break;
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadCourses(),
            this.loadAssignments(),
            this.loadGrades()
        ]);
    }

    async loadCourses() {
        try {
            const response = await fetch('/api/teacher/courses');
            if (!response.ok) throw new Error('Error al cargar los cursos');

            const data = await response.json();
            this.updateCoursesUI(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async loadAssignments() {
        try {
            const response = await fetch('/api/teacher/assignments');
            if (!response.ok) throw new Error('Error al cargar las tareas');

            const data = await response.json();
            this.updateAssignmentsUI(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async loadGrades() {
        try {
            const response = await fetch('/api/teacher/grades');
            if (!response.ok) throw new Error('Error al cargar las calificaciones');

            const data = await response.json();
            this.updateGradesTable(data);
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    updateCoursesUI(courses) {
        const container = document.getElementById('courses-container');
        if (!container) return;

        container.innerHTML = courses.map(course => this.createCourseCard(course)).join('');
    }

    updateAssignmentsUI(assignments) {
        const container = document.getElementById('assignments-container');
        if (!container) return;

        container.innerHTML = assignments.map(assignment => this.createAssignmentRow(assignment)).join('');
    }

    updateGradesTable(grades) {
        const tbody = document.querySelector('#grades-table tbody');
        if (!tbody) return;

        tbody.innerHTML = grades.map(grade => this.createGradeRow(grade)).join('');
    }

    createCourseCard(course) {
        return `
            <div class="col-md-6 col-xl-4 mb-4">
                <div class="course-card">
                    <div class="course-header">
                        <h6 class="course-name">${course.name}</h6>
                        <span class="course-code">${course.code}</span>
                    </div>
                    <div class="course-body">
                        <p class="course-stats">
                            <span><i class="fas fa-users"></i> ${course.students_count} estudiantes</span>
                            <span><i class="fas fa-tasks"></i> ${course.assignments_count} tareas</span>
                        </p>
                        <div class="course-progress">
                            <div class="progress">
                                <div class="progress-bar" style="width: ${course.progress}%"></div>
                            </div>
                            <span class="progress-text">${course.progress}% completado</span>
                        </div>
                    </div>
                    <div class="course-actions">
                        <a href="/teacher/courses/${course.id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    createAssignmentRow(assignment) {
        return `
            <tr>
                <td>${assignment.title}</td>
                <td>${assignment.course_name}</td>
                <td>${assignment.due_date}</td>
                <td>
                    <span class="badge bg-${assignment.status_color}">
                        ${assignment.status}
                    </span>
                </td>
                <td>${assignment.submissions_count}/${assignment.total_students}</td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-primary" onclick="teacherProfile.viewAssignment('${assignment.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-info" onclick="teacherProfile.editAssignment('${assignment.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="teacherProfile.deleteAssignment('${assignment.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    createGradeRow(grade) {
        return `
            <tr>
                <td>${grade.student_name}</td>
                <td>${grade.course_name}</td>
                <td>${grade.average}</td>
                <td>${grade.completed_assignments}/${grade.total_assignments}</td>
                <td>${grade.last_activity}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="teacherProfile.viewStudentGrades('${grade.student_id}')">
                        <i class="fas fa-chart-line"></i> Ver Detalle
                    </button>
                </td>
            </tr>
        `;
    }

    async viewAssignment(id) {
        // Implementar vista detallada de tarea
    }

    async editAssignment(id) {
        // Implementar edición de tarea
    }

    async deleteAssignment(id) {
        if (!confirm('¿Está seguro de que desea eliminar esta tarea?')) return;

        try {
            const response = await fetch(`/api/teacher/assignments/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Error al eliminar la tarea');

            document.querySelector(`tr[data-assignment-id="${id}"]`)?.remove();
            this.showToast('Tarea eliminada exitosamente', 'success');
        } catch (error) {
            this.showToast(error.message, 'error');
        }
    }

    async viewStudentGrades(studentId) {
        // Implementar vista detallada de calificaciones del estudiante
    }

    showToast(message, type = 'info') {
        // Usar el sistema de notificaciones global
        if (window.showNotification) {
            window.showNotification(message, type);
        }
    }
}

// Inicializar el perfil del profesor
const teacherProfile = new TeacherProfile(); 