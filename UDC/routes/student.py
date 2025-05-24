import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, send_file
from bson import ObjectId

from routes.auth import login_required, role_required
from models import Event, Grade, Course, InstitutionalFile

student = Blueprint('student', __name__)

@student.route('/')  
@login_required  
@role_required('student')  
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

@student.route('/events')  
@login_required  
@role_required('student')  
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

@student.route('/grades')
@login_required
@role_required('student')
def grades():
    student_id = session.get('user_id')
    grades = Grade.find_by_student(student_id)
    return render_template('student/grades.html', grades=grades)

# 🔽 NUEVAS RUTAS DE ARCHIVOS 🔽

@student.route('/files')
@login_required
@role_required('student')
def view_files():
    # Solo archivos académicos para estudiantes
    files = InstitutionalFile.find_by_category('academic')
    return render_template('student/files.html', files=files)

@student.route('/files/download/<file_id>')
@login_required
@role_required('student')
def download_file(file_id):
    try:
        # Solo permitir descarga de archivos académicos
        file_doc = InstitutionalFile.collection.find_one({
            '_id': ObjectId(file_id),
            'category': 'academic',
            'active': True
        })

        if not file_doc:
            flash('Archivo no encontrado o no autorizado', 'error')
            return redirect(url_for('student.view_files'))

        file_path = os.path.join(current_app.root_path, file_doc['file_path'])

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True,
                             download_name=f"{file_doc['title']}.{file_doc['file_type']}")
        else:
            flash('Archivo no disponible', 'error')
            return redirect(url_for('student.view_files'))

    except Exception as e:
        flash('Error al acceder al archivo', 'error')
        return redirect(url_for('student.view_files'))
