from flask import Blueprint, render_template, session, redirect, url_for, flash  
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