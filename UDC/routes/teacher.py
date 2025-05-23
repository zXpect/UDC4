import os
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file
from werkzeug.utils import secure_filename
from bson import ObjectId

from routes.auth import login_required, role_required
from models import Grade, Course, InstitutionalFile, User

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}

teacher = Blueprint('teacher', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@teacher.route('/')
@login_required
@role_required('teacher')
def dashboard():
    teacher_id = session.get('user_id')
    courses = Course.find_all()
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

        if not title or not description or not category:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename

            upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            os.makedirs(upload_path, exist_ok=True)

            file_path = os.path.join(upload_path, filename)
            file.save(file_path)

            file_type = filename.rsplit('.', 1)[1].lower()
            relative_path = os.path.join(UPLOAD_FOLDER, filename)

            file_id = InstitutionalFile.create(
                title, description, relative_path, file_type,
                session.get('user_id'), category
            )

            if file_id:
                flash('Archivo subido exitosamente', 'success')
            else:
                flash('Error al guardar el archivo', 'error')
        else:
            flash('Tipo de archivo no permitido', 'error')

    files = InstitutionalFile.find_all()
    return render_template('teacher/files.html', files=files)

#Ruta para descarga de archivos
@teacher.route('/files/download/<file_id>')
@login_required
@role_required('teacher')
def download_file(file_id):
    try:
        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id)})
        if not file_doc:
            flash('Archivo no encontrado', 'error')
            return redirect(url_for('teacher.manage_files'))

        file_path = os.path.join(current_app.root_path, file_doc['file_path'])

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True,
                             download_name=f"{file_doc['title']}.{file_doc['file_type']}")
        else:
            flash('Archivo físico no encontrado', 'error')
            return redirect(url_for('teacher.manage_files'))

    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('teacher.manage_files'))
