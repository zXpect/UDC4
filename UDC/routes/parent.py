import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, send_file, jsonify
from bson import ObjectId
from models import Event, StudentParentRelation, Grade, InstitutionalFile, User

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
    parent_id = session.get('user_id')
    # Parents see files based on their role
    files = InstitutionalFile.find_all_for_role('parent', parent_id)
    return render_template('parent/academic_files.html', files=files)

@parent.route('/files/download/<file_id_str>')
@login_required
@role_required('parent')
def download_file(file_id_str):
    user_role = session.get('role') # Should be 'parent'
    user_id = session.get('user_id')
    try:
        if not ObjectId.is_valid(file_id_str):
            flash('ID de archivo inválido.', 'error')
            return redirect(url_for('parent.academic_files'))

        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})

        if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
            flash('Acceso denegado o archivo no encontrado.', 'error')
            return redirect(url_for('parent.academic_files'))

        file_path_relative = file_doc['file_path']
        file_path_absolute = os.path.join(current_app.root_path, file_path_relative)

        if os.path.exists(file_path_absolute):
            download_name = f"{file_doc.get('title', 'archivo')}.{file_doc.get('file_type', 'bin')}"
            return send_file(file_path_absolute, as_attachment=True, download_name=download_name)
        else:
            flash('Archivo físico no disponible en el servidor.', 'error')
            current_app.logger.error(f"Physical file not found: {file_path_absolute} for InstitutionalFile ID: {file_id_str}")
            return redirect(url_for('parent.academic_files'))

    except Exception as e:
        current_app.logger.error(f"Error parent downloading file ID {file_id_str}: {e}")
        flash('Error al acceder al archivo.', 'error')
        return redirect(url_for('parent.academic_files'))

@parent.route('/files/details_json/<file_id_str>')
@login_required
@role_required('parent')
def get_parent_file_details_json(file_id_str):
    user_role = session.get('role') # Should be 'parent'
    user_id = session.get('user_id') # Parent's ID

    if not ObjectId.is_valid(file_id_str):
        return jsonify({'success': False, 'error': 'ID de archivo inválido'}), 400

    file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})

    if not file_doc:
        return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404

    # Check if parent can access this file (e.g. category is general or academic)
    if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
        return jsonify({'success': False, 'error': 'Acceso denegado'}), 403

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
                 file_details['uploader_role'] = 'Admin.'
            else:
                 file_details['uploader_role'] = uploader.get('role', '').title()
        else:
            file_details['uploader_name'] = 'Desconocido'
    else:
        file_details['uploader_name'] = 'Sistema'

    return jsonify({'success': True, 'file': file_details})
