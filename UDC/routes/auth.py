from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models import User, UserNotification, Course, CourseEnrollment, Grade, Task, Attendance
import datetime
import re

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            if user_role not in roles:
                flash('Acceso denegado. No tienes permisos para acceder a esta página.', 'error')
                return redirect(url_for('public.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def student_required(f):  
    @wraps(f)  
    def decorated_function(*args, **kwargs):  
        if not session.get('logged_in') or session.get('role') != 'student':  
            flash('Acceso denegado', 'error')  
            return redirect(url_for('auth.login'))  
        return f(*args, **kwargs)  
    return decorated_function  
  
def parent_required(f):  
    @wraps(f)  
    def decorated_function(*args, **kwargs):  
        if not session.get('logged_in') or session.get('role') != 'parent':  
            flash('Acceso denegado', 'error')  
            return redirect(url_for('auth.login'))  
        return f(*args, **kwargs)  
    return decorated_function  
  
def teacher_required(f):  
    @wraps(f)  
    def decorated_function(*args, **kwargs):  
        if not session.get('logged_in') or session.get('role') != 'teacher':  
            flash('Acceso denegado', 'error')  
            return redirect(url_for('auth.login'))  
        return f(*args, **kwargs)  
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Validaciones básicas
        if not username or not password:
            flash('Usuario y contraseña son obligatorios', 'danger')
            return render_template('auth/login.html', error="Usuario y contraseña son obligatorios")
        
        # Verificar credenciales
        user = User.verify_password(username, password)
        if user:
            # Configurar sesión
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['email'] = user.get('email', '')
            session['first_name'] = user.get('first_name', '')
            session['last_name'] = user.get('last_name', '')
            session['role'] = user['role']
            session['logged_in'] = True
            session['avatar_url'] = user.get('avatar_url', '')
            
            # Configurar duración de sesión
            if remember:
                session.permanent = True
            
            # Actualizar estadísticas de login
            try:
                User.collection.update_one(
                    {'_id': user['_id']},
                    {
                        '$set': {'stats.last_login': datetime.datetime.utcnow()},
                        '$inc': {'stats.login_count': 1}
                    }
                )
            except Exception as e:
                print(f"Error updating login stats: {e}")
            
# Redirección según rol  
            if user['role'] == 'admin':  
                return redirect(url_for('admin.dashboard'))  
            elif user['role'] == 'student':  
                return redirect(url_for('student.dashboard'))  
            elif user['role'] == 'parent':  
                return redirect(url_for('parent.dashboard'))  
            elif user['role'] == 'teacher':  
                return redirect(url_for('teacher.dashboard'))  
            else:  
                return redirect(url_for('public.index'))
        else:
            # Credenciales incorrectas
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('auth/login.html', error="Usuario o contraseña incorrectos")
    
    # Si ya está logueado, redirigir  
    if session.get('logged_in'):  
        user_role = session.get('role')  
        if user_role == 'admin':  
            return redirect(url_for('admin.dashboard'))  
        elif user_role == 'student':  
            return redirect(url_for('student.dashboard'))  
        elif user_role == 'parent':  
            return redirect(url_for('parent.dashboard'))  
        elif user_role == 'teacher':  
            return redirect(url_for('teacher.dashboard'))  
        else:  
            return redirect(url_for('public.index'))
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')
        role = request.form.get('role', 'student')
        terms = request.form.get('terms') == 'on'
        newsletter = request.form.get('newsletter') == 'on'
        
        # Validaciones básicas
        errors = []
        
        if not all([first_name, last_name, email, username, password, confirm_password, role]):
            errors.append('Todos los campos obligatorios deben ser completados')
        
        if not terms:
            errors.append('Debes aceptar los términos y condiciones')
        
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden')
        
        # Verificar disponibilidad
        if User.find_by_username(username):
            errors.append('El nombre de usuario ya existe')
        
        if User.find_by_email(email):
            errors.append('El correo electrónico ya está registrado')
        
        # Si hay errores, mostrarlos
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Crear nuevo usuario
        try:
            # Simplificamos la validación para asegurar que funcione
            user_id = User.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            flash('Usuario registrado exitosamente. Puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('auth/register.html')
        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            flash('Error al registrar usuario. Por favor intenta nuevamente.', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Obtener información completa del usuario
    user = User.find_by_id(session.get('user_id'))
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        # Actualizar configuraciones
        settings_data_from_form = { # Renamed to avoid conflict
            'theme': request.form.get('theme', 'light'),
            'email_notifications': request.form.get('email_notifications') == 'on'
        }
        
        try:
            User.collection.update_one(
                {'_id': user['_id']},
                {'$set': {'settings': settings_data_from_form}}
            )
            flash('Configuraciones actualizadas exitosamente', 'success')
        except Exception as e:
            flash('Error al actualizar las configuraciones', 'danger')
            print(f"Error updating settings: {e}")
        
        return redirect(url_for('auth.profile'))
    
    # Preparar datos del usuario para el template
    user_data = {
        'user_id': str(user['_id']),
        'username': user['username'],
        'email': user.get('email', ''),
        'first_name': user.get('first_name', ''),
        'last_name': user.get('last_name', ''),
        'role': user['role'],
        'phone': user.get('phone', ''),
        'birth_date': user.get('birth_date', ''),
        'gender': user.get('gender', ''),
        'address': user.get('address', ''),
        'bio': user.get('bio', ''),
        'avatar_url': user.get('avatar_url', ''),
        'created_at': user.get('created_at', ''),
        'stats': user.get('stats', {}),
        'settings': user.get('settings', {'theme': 'light', 'email_notifications': True}) # This is user.settings
    }

    # Prepare user_settings for the modal, consistent across profiles
    user_settings_for_modal = {
        'theme': user_data['settings'].get('theme', 'light'),
        'email_notifications': user_data['settings'].get('email_notifications', True) # Default to True if not found
    }

    if user['role'] == 'admin':
        return render_template('admin/profile_admin.html', user=user_data, user_settings=user_settings_for_modal)
    elif user['role'] == 'student':
        return render_template('admin/profile_student.html', user=user_data, user_settings=user_settings_for_modal)
    elif user['role'] == 'parent':
        return render_template('admin/profile_parent.html', user=user_data, user_settings=user_settings_for_modal)
    elif user['role'] == 'teacher':
        teacher_id = session.get('user_id')
        
        # Datos para el resumen general
        courses = Course.find_by_teacher_id(teacher_id)
        total_students = 0
        for course_item in courses: # Renamed to avoid conflict with courses variable name
            total_students += len(CourseEnrollment.get_students_by_course(str(course_item['_id'])))
        
        pending_tasks_count = Task.collection.count_documents({
            'teacher_id': user['_id'], 
            'due_date': {'$gte': datetime.datetime.utcnow()},
            'active': True 
        })

        stats_overview = {
            'total_courses': len(courses),
            'total_students': total_students,
            'pending_tasks': pending_tasks_count, 
            'upcoming_events': 2 
        }

        # Datos para "Mis Cursos"
        teacher_courses_data = []
        for course_item in courses: # Renamed to avoid conflict
            course_dict = dict(course_item)
            students_in_course = CourseEnrollment.get_students_by_course(str(course_item['_id']))
            grades = list(Grade.collection.find({'course_id': course_item['_id']}))
            grade_values = [float(g['grade_value']) for g in grades if 'grade_value' in g]
            avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0

            course_dict.update({
                'students_count': len(students_in_course),
                'average_grade': round(avg_grade, 2),
                'next_class_date': 'Pendiente', 
                'icon': 'book' 
            })
            teacher_courses_data.append(course_dict)

        # Datos para "Mi Horario" (Ejemplo)
        schedule_data = {
            'Monday': [{'time': '08:00 - 09:30', 'course_name': 'Matemáticas 3A', 'room': 'A101'}],
            'Tuesday': [{'time': '10:00 - 11:30', 'course_name': 'Álgebra 5B', 'room': 'B203'}],
        }
        
        # Datos para "Tareas y Calificaciones"
        tasks = Task.find_by_teacher_id_with_course_info(teacher_id)
        recent_grades = Grade.find_by_teacher(teacher_id)[:5] 
        
        # Datos para "Comunicación" (Ejemplo)
        recent_messages = [
            {'sender': 'Admin', 'subject': 'Reunión Importante', 'date': 'Hace 2 horas'},
            {'sender': 'Juan Pérez (Padre)', 'subject': 'Consulta sobre Matías', 'date': 'Ayer'}
        ]
        
        return render_template('admin/profile_teacher.html', 
                               user=user_data, 
                               user_settings=user_settings_for_modal, # Pass the correct settings variable
                               stats_overview=stats_overview,
                               teacher_courses=teacher_courses_data,
                               schedule_data=schedule_data,
                               tasks=tasks,
                               recent_grades=recent_grades,
                               recent_messages=recent_messages
                               )
    else:
        return redirect(url_for('public.index'))

@auth.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('public.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperación de contraseña"""
    if request.method == 'POST':
        email = request.form.get('resetEmail', '').strip().lower()
        
        if not email:
            flash('Email requerido', 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.find_by_email(email)
        if user:
            # Aquí implementarías la lógica para enviar email de recuperación
            # Por ahora, simularemos que se envió
            flash('Se ha enviado un enlace de recuperación a tu correo electrónico', 'success')
        else:
            # Por seguridad, no revelamos si el email existe o no
            flash('Si el correo existe, recibirás un enlace de recuperación', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

# Función auxiliar para obtener información del usuario actual
def get_current_user():
    """Obtener información del usuario actual de la sesión"""
    if not session.get('logged_in'):
        return None
    
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'email': session.get('email'),
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'role': session.get('role'),
        'avatar_url': session.get('avatar_url', '')
    }

# Context processor para hacer disponible la información del usuario en todos los templates
@auth.app_context_processor
def inject_user():
    return dict(current_user=get_current_user())
