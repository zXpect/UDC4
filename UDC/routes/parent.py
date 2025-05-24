import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, send_file
from bson import ObjectId
from models import Event, StudentParentRelation, Grade, InstitutionalFile

from routes.auth import login_required, role_required
from models import StudentParentRelation, Grade, InstitutionalFile
import datetime
parent = Blueprint('parent', __name__)

@parent.route('/')  
@login_required  
@role_required('parent')  
def dashboard():  
    parent_id = session.get('user_id')  
      
    # Obtener hijos del padre  
    children = StudentParentRelation.find_children_by_parent(parent_id)  
    events = Event.find_all()[:5]  # Próximos 5 eventos  
      
    # Procesar eventos para convertir fechas string a datetime  
    processed_events = []  
    for event in events:  
        event_dict = dict(event)  
        if isinstance(event.get('date'), str):  
            try:  
                event_dict['date'] = datetime.datetime.strptime(event['date'], '%Y-%m-%d')  
            except ValueError:  
                event_dict['date'] = None # O manejar el error como prefieras  
        processed_events.append(event_dict)  
  
    # Calcular estadísticas de todos los hijos (código ya proporcionado)  
    total_grades = 0  
    all_grade_values = []  
      
    children_with_stats = []  
    for child in children:  
        child_grades = Grade.find_by_student(child['_id'])  
          
        child_grade_values = []  
        for g in child_grades:  
            try:  
                grade_val = float(g.get('grade_value', 0))  
                child_grade_values.append(grade_val)  
                all_grade_values.append(grade_val)  
            except (ValueError, TypeError):  
                continue  
          
        child_avg = sum(child_grade_values) / len(child_grade_values) if child_grade_values else 0  
          
        child_data = dict(child)  
        child_data['avg_grade'] = round(child_avg, 1) if child_avg > 0 else 'N/A'  
        children_with_stats.append(child_data)  
          
        total_grades += len(child_grades)  
      
    avg_grade = sum(all_grade_values) / len(all_grade_values) if all_grade_values else 0  
      
    stats = {  
        'avg_grade': round(avg_grade, 1) if avg_grade > 0 else 'N/A',  
        'total_grades': total_grades,  
        'upcoming_events': len(processed_events) # Usar processed_events aquí  
    }  
      
    return render_template('parent/dashboard.html',   
                         children=children_with_stats,  
                         stats=stats,  
                         upcoming_events=processed_events)
@parent.route('/child/<child_id>/grades')
@login_required
@role_required('parent')
def child_grades(child_id):
    # Verificar que el padre tiene acceso a este estudiante
    parent_id = session.get('user_id')
    children = StudentParentRelation.find_children_by_parent(parent_id)
    child_ids = [str(child['_id']) for child in children]

    if child_id not in child_ids:
        flash('Acceso denegado', 'error')
        return redirect(url_for('parent.dashboard'))

    grades = Grade.find_by_student(child_id)
    return render_template('parent/child_grades.html', grades=grades, child_id=child_id)

@parent.route('/academic-files')
@login_required
@role_required('parent')
def academic_files():
    files = InstitutionalFile.find_by_category('academic')
    return render_template('parent/academic_files.html', files=files)

@parent.route('/files/download/<file_id>')
@login_required
@role_required('parent')
def download_file(file_id):
    try:
        # Solo permitir descarga de archivos académicos
        file_doc = InstitutionalFile.collection.find_one({
            '_id': ObjectId(file_id),
            'category': 'academic',
            'active': True
        })

        if not file_doc:
            flash('Archivo no encontrado', 'error')
            return redirect(url_for('parent.academic_files'))

        file_path = os.path.join(current_app.root_path, file_doc['file_path'])

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True,
                             download_name=f"{file_doc['title']}.{file_doc['file_type']}")
        else:
            flash('Archivo no disponible', 'error')
            return redirect(url_for('parent.academic_files'))

    except Exception as e:
        flash('Error al acceder al archivo', 'error')
        return redirect(url_for('parent.academic_files'))
