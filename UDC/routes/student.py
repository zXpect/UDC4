import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, send_file, jsonify
from bson import ObjectId
from functools import wraps

from routes.auth import login_required, role_required
from models import Event, Grade, Course, InstitutionalFile, CourseEnrollment, User

student = Blueprint('student', __name__, url_prefix='/student')

# Decorator to ensure user is logged in and is a student
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'student':
            flash('Debes iniciar sesión como estudiante para acceder a esta página.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student.route('/')
@student_required
def dashboard():
    student_id = session.get('user_id')
    
    grades = Grade.find_by_student(student_id)
    events = Event.find_all()[:5]
    academic_files = InstitutionalFile.find_by_category('academic')
    
    # Convertir calificaciones a float de manera segura
    grade_values = []
    for g in grades:
        try:
            grade_val = float(g.get('grade_value', 0))
            grade_values.append(grade_val)
        except (ValueError, TypeError):
            continue
    
    avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0
    
    stats = {
        'avg_grade': round(avg_grade, 1) if avg_grade > 0 else 0,
        'total_grades': len(grades),
        'available_files': len(academic_files),
        'upcoming_events': len(events)
    }
    
    # Procesar eventos para evitar errores de strftime
    processed_events = []
    for event in events:
        event_dict = dict(event)
        # Asegurar que date sea un objeto datetime
        if isinstance(event.get('date'), str):
            try:
                from datetime import datetime
                event_dict['date'] = datetime.strptime(event['date'], '%Y-%m-%d')
            except:
                event_dict['date'] = None
        processed_events.append(event_dict)
    
    return render_template('student/dashboard.html',
                         stats=stats,
                         recent_grades=grades[:10],
                         upcoming_events=processed_events)

@student.route('/my-courses')
@student_required
def my_courses():
    student_id = session.get('user_id')
    if not student_id:
        flash('No se pudo identificar al estudiante.', 'error')
        return redirect(url_for('student.dashboard'))
    
    enrolled_courses = CourseEnrollment.get_courses_by_student(student_id)
    
    return render_template('student/my_courses.html', courses=enrolled_courses)

@student.route('/grades')
@student_required
def grades():
    student_id = session.get('user_id')
    grades_raw = Grade.find_by_student(student_id)
    
    grades_data = []
    for grade in grades_raw:
        grade_dict = dict(grade) # Convert to dict for modification
        course = Course.collection.find_one({'_id': grade['course_id']})
        grade_dict['course_name'] = course['name'] if course else 'Curso Desconocido'
        
        # Ensure grade_value is a float for consistent formatting
        try:
            grade_dict['grade_value'] = float(str(grade_dict.get('grade_value', '0')).replace(',', '.'))
        except ValueError:
            grade_dict['grade_value'] = 0.0 # Default to 0.0 if conversion fails
            
        grades_data.append(grade_dict)
        
    return render_template('student/grades.html', grades=grades_data)

@student.route('/events')
@student_required
def events():
    events = Event.find_all()
    
    # Procesar eventos para convertir fechas string a datetime
    processed_events = []
    for event in events:
        event_dict = dict(event)
        # Asegurar que date sea un objeto datetime
        if isinstance(event.get('date'), str):
            try:
                from datetime import datetime
                event_dict['date'] = datetime.strptime(event['date'], '%Y-%m-%d')
            except:
                event_dict['date'] = None
        processed_events.append(event_dict)
    
    return render_template('student/events.html', events=processed_events)

@student.route('/view_files')
@student_required
def view_files():
    student_id = session.get('user_id')
    # Students see files based on their role
    files = InstitutionalFile.find_all_for_role('student', student_id)
    return render_template('student/view_files.html', files=files)

@student.route('/files/download/<file_id_str>')
@login_required # student_required implies login_required but let's be explicit
@role_required('student') # Ensure it's a student making the request initially
def download_file(file_id_str):
    user_role = session.get('role') # Should be 'student'
    user_id = session.get('user_id')
    
    try:
        if not ObjectId.is_valid(file_id_str):
            flash('ID de archivo inválido.', 'error')
            return redirect(url_for('student.view_files'))

        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})
        
        if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
            flash('Acceso denegado o archivo no encontrado.', 'error')
            return redirect(url_for('student.view_files'))

        file_path_relative = file_doc['file_path']
        file_path_absolute = os.path.join(current_app.root_path, file_path_relative)

        if os.path.exists(file_path_absolute):
            download_name = f"{file_doc.get('title', 'archivo')}.{file_doc.get('file_type', 'bin')}"
            return send_file(file_path_absolute, as_attachment=True, download_name=download_name)
        else:
            flash('Archivo físico no disponible en el servidor.', 'error')
            current_app.logger.error(f"Physical file not found: {file_path_absolute} for InstitutionalFile ID: {file_id_str}")
            return redirect(url_for('student.view_files'))

    except Exception as e:
        current_app.logger.error(f"Error student downloading file ID {file_id_str}: {e}")
        flash('Error al acceder al archivo.', 'error')
        return redirect(url_for('student.view_files'))

@student.route('/files/details_json/<file_id_str>')
@student_required # Ensures student is logged in
def get_student_file_details_json(file_id_str):
    user_role = session.get('role') # Should be 'student'
    user_id = session.get('user_id')

    if not ObjectId.is_valid(file_id_str):
        return jsonify({'success': False, 'error': 'ID de archivo inválido'}), 400

    file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})

    if not file_doc:
        return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404

    if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
        return jsonify({'success': False, 'error': 'Acceso denegado'}), 403

    # Prepare data for JSON response
    file_details = {
        'id': str(file_doc['_id']),
        'title': file_doc.get('title', 'N/A'),
        'description': file_doc.get('description', 'Sin descripción.'),
        'category': file_doc.get('category', 'N/A'),
        'file_type': file_doc.get('file_type', 'N/A'),
        'created_at': file_doc.get('created_at').strftime('%d/%m/%Y %H:%M') if file_doc.get('created_at') else 'N/A',
    }
    # Add uploader name (e.g., teacher or admin)
    if file_doc.get('uploaded_by'):
        uploader = User.find_by_id(file_doc['uploaded_by'])
        if uploader:
            uploader_name = f"{uploader.get('first_name', '')} {uploader.get('last_name', '')}".strip()
            file_details['uploader_name'] = uploader_name if uploader_name else 'Desconocido'
            if uploader.get('role') == 'teacher':
                 file_details['uploader_role'] = 'Profesor'
            elif uploader.get('role') == 'admin':
                 file_details['uploader_role'] = 'Admin.' # Short for Admin
            else:
                 file_details['uploader_role'] = uploader.get('role', '').title()
        else:
            file_details['uploader_name'] = 'Desconocido'
    else:
        file_details['uploader_name'] = 'Sistema'

    return jsonify({'success': True, 'file': file_details})
