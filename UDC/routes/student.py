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
    events = Event.find_all()[:5]  # Últimos 5 eventos
    student_id = session.get('user_id')
    grades = Grade.find_by_student(student_id)
    
    return render_template('student/dashboard.html', events=events, grades=grades)

@student.route('/events')
@login_required
@role_required('student')
def events():
    events = Event.find_all()
    return render_template('student/events.html', events=events)

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
