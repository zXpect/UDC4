from flask import Blueprint, render_template, request, redirect, url_for, flash, session  
from routes.auth import login_required, role_required  
from models import Grade, Course, InstitutionalFile, User  
  
teacher = Blueprint('teacher', __name__)  
  
@teacher.route('/')  
@login_required  
@role_required('teacher')  
def dashboard():  
    teacher_id = session.get('user_id')  
    courses = Course.find_all()  # Filtrar por profesor en producción  
    recent_grades = Grade.find_by_teacher(teacher_id)[:10]  
    return render_template('teacher/dashboard.html', courses=courses, recent_grades=recent_grades)  
  
@teacher.route('/grades', methods=['GET', 'POST'])  
@login_required  
@role_required('teacher')  
def manage_grades():  
    if request.method == 'POST':  
        student_id = request.form.get('student_id')  
        course_id = request.form.get('course_id')  
        grade_value = request.form.get('grade_value')  
        grade_type = request.form.get('grade_type')  
        description = request.form.get('description', '')  
        teacher_id = session.get('user_id')  
          
        if all([student_id, course_id, grade_value, grade_type]):  
            Grade.create(student_id, course_id, teacher_id, grade_value, grade_type, description)  
            flash('Nota registrada exitosamente', 'success')  
        else:  
            flash('Todos los campos son obligatorios', 'error')  
      
    students = User.collection.find({'role': 'student', 'active': True})  
    courses = Course.find_all()  
    return render_template('teacher/grades.html', students=students, courses=courses)  
  
@teacher.route('/files', methods=['GET', 'POST'])  
@login_required  
@role_required('teacher')  
def manage_files():  
    if request.method == 'POST':  
        title = request.form.get('title')  
        description = request.form.get('description')  
        category = request.form.get('category')  
        file_path = '/uploads/placeholder.pdf'
          
        if title and description:  
            InstitutionalFile.create(title, description, file_path, 'pdf', session.get('user_id'), category)  
            flash('Archivo subido exitosamente', 'success')  
      
    files = InstitutionalFile.find_all()  
    return render_template('teacher/files.html', files=files)