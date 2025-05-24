import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, send_file
from bson import ObjectId

from routes.auth import login_required, role_required
from models import StudentParentRelation, Grade, InstitutionalFile

parent = Blueprint('parent', __name__)

@parent.route('/')
@login_required
@role_required('parent')
def dashboard():
    parent_id = session.get('user_id')
    children = StudentParentRelation.find_children_by_parent(parent_id)
    return render_template('parent/dashboard.html', children=children)

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
