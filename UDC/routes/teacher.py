import os
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file, jsonify, make_response
from werkzeug.utils import secure_filename
from bson import ObjectId
import pdfkit

from routes.auth import login_required, role_required
from models import Grade, Course, InstitutionalFile, User, CourseEnrollment, Task, Attendance

UPLOAD_FOLDER = 'static/uploads'
UPLOAD_FOLDER_TASKS = os.path.join(UPLOAD_FOLDER, 'tasks')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'txt', 'zip', 'ppt', 'pptx'}

teacher = Blueprint('teacher', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@teacher.route('/')  
@login_required  
@role_required('teacher')  
def dashboard():  
    teacher_id = session.get('user_id')  
      
    # Obtener datos reales  
    courses = Course.find_all()  
    recent_grades = Grade.find_by_teacher(teacher_id)[:10]  
      
    # Estadísticas del profesor  
    total_students = len(User.collection.find({'role': 'student', 'active': True}).distinct('_id'))  
    total_courses = len(courses)  
    pending_grades = len([g for g in recent_grades if not g.get('graded', True)])  
      
    # Calcular promedio general - CORREGIR AQUÍ  
    all_grades = Grade.find_by_teacher(teacher_id)  
    # Convertir a float antes de sumar  
    grade_values = []  
    for g in all_grades:  
        try:  
            grade_val = float(g.get('grade_value', 0))  
            grade_values.append(grade_val)  
        except (ValueError, TypeError):  
            continue  
      
    avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0  
      
    stats = {  
        'total_students': total_students,  
        'total_courses': total_courses,  
        'pending_grades': pending_grades,  
        'avg_grade': round(avg_grade, 1)  
    }  
      
    return render_template('teacher/dashboard.html',   
                         courses=courses,   
                         recent_grades=recent_grades,  
                         stats=stats)

@teacher.route('/my-courses')
@login_required
@role_required('teacher')
def my_courses():
    teacher_id = session.get('user_id')
    courses = Course.find_by_teacher_id(teacher_id)
    
    # Obtener estadísticas de cada curso
    courses_with_stats = []
    for course in courses:
        course_dict = dict(course)
        enrolled_students = CourseEnrollment.get_students_by_course(str(course['_id']))
        grades = Grade.collection.find({'course_id': course['_id']})
        
        # Calcular promedio del curso
        grade_values = [float(g['grade_value']) for g in grades if 'grade_value' in g]
        avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0
        
        course_dict.update({
            'student_count': len(enrolled_students),
            'average_grade': round(avg_grade, 2),
            'next_class_date': 'Próxima clase pendiente'  # Esto se podría obtener de un sistema de horarios
        })
        courses_with_stats.append(course_dict)
    
    return render_template('teacher/my_courses.html', courses=courses_with_stats)

@teacher.route('/tasks')
@login_required
@role_required('teacher')
def manage_tasks():
    teacher_id = session.get('user_id')
    tasks = Task.find_by_teacher_id_with_course_info(teacher_id)
    current_time = datetime.datetime.utcnow()
    return render_template('teacher/manage_tasks.html', tasks=tasks, now=current_time)

@teacher.route('/tasks/add', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def add_task():
    teacher_id = session.get('user_id')
    teacher_courses = Course.find_by_teacher_id(teacher_id)

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        file_path_for_db = None
        task_file_id = None # To store the ID of the InstitutionalFile record for the task
        uploaded_file = request.files.get('task_file')

        if not all([course_id, title, description, due_date_str]):
            flash('Por favor, complete todos los campos obligatorios: Materia, Título, Descripción y Fecha de Entrega.', 'error')
            return render_template('teacher/task_form.html', courses=teacher_courses, task={},
                                   action=url_for('teacher.add_task'))
        
        try:
            # Create the task first to get its ID
            task_instance_id = Task.create(course_id, teacher_id, title, description, due_date_str, file_path=None) # File path set later

            if uploaded_file and uploaded_file.filename != '' :
                if allowed_file(uploaded_file.filename):
                    filename = secure_filename(uploaded_file.filename)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    unique_filename = f"{timestamp}_{filename}"
                    
                    course_task_upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER_TASKS)
                    os.makedirs(course_task_upload_path, exist_ok=True)
                    
                    file_save_path = os.path.join(course_task_upload_path, unique_filename)
                    uploaded_file.save(file_save_path)
                    file_path_for_db = os.path.join(UPLOAD_FOLDER_TASKS, unique_filename) # Relative path

                    # Create an InstitutionalFile record for the task attachment
                    task_file_id = InstitutionalFile.create(
                        title=f"Adjunto: {title}", 
                        description=f"Archivo adjunto para la tarea '{title}'",
                        file_path=file_path_for_db,
                        file_type=uploaded_file.mimetype, # Or extract extension
                        uploaded_by=teacher_id,
                        category='tasks', # Special category for task files
                        related_task_id=str(task_instance_id) 
                    )
                    # Update the task with the actual file_path (which is now relative)
                    Task.update(str(task_instance_id), {'file_path': file_path_for_db})

                else:
                    # If file is not allowed, delete the partially created task
                    Task.delete(str(task_instance_id)) # Soft delete
                    flash('Tipo de archivo no permitido.', 'error')
                    return render_template('teacher/task_form.html', courses=teacher_courses, task=request.form, 
                                           action=url_for('teacher.add_task'))
            
            flash('Tarea creada exitosamente.', 'success')
            return redirect(url_for('teacher.manage_tasks'))
        except ValueError as ve:
            # If task creation failed before file handling, task_instance_id might not exist or be valid
            flash(str(ve), 'error')
        except Exception as e:
            current_app.logger.error(f"Error creating task or handling file: {e}")
            # Clean up if task was created but file handling failed
            if 'task_instance_id' in locals() and task_instance_id:
                Task.delete(str(task_instance_id)) # Attempt to soft delete
            flash(f'Error al crear la tarea: {e}', 'error')
        
        return render_template('teacher/task_form.html', courses=teacher_courses, task={},
                           action=url_for('teacher.add_task'))

    return render_template('teacher/task_form.html', courses=teacher_courses, task={},
                           action=url_for('teacher.add_task'))

@teacher.route('/tasks/edit/<task_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def edit_task(task_id):
    task = Task.find_by_id(task_id)
    if not task:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

    if task['teacher_id'] != ObjectId(session.get('user_id')):
        flash('No tienes permiso para editar esta tarea.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

    teacher_id = session.get('user_id')
    teacher_courses = Course.find_by_teacher_id(teacher_id)
    
    # Find existing institutional file for this task, if any
    existing_institutional_file = None
    if task.get('file_path'):
        # Assuming file_path stored in task is the unique identifier or part of it for InstitutionalFile
        # A more robust way would be to store institutional_file_id in the Task model.
        # For now, let's try to find it by related_task_id.
        existing_institutional_file_doc = InstitutionalFile.collection.find_one({
            'related_task_id': ObjectId(task_id), 
            'active': True
        })


    if request.method == 'POST':
        course_id = request.form.get('course_id')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        current_file_path = task.get('file_path')
        new_file_path_for_db = current_file_path # Keep existing file path by default
        uploaded_file = request.files.get('task_file')

        if not all([course_id, title, description, due_date_str]):
            flash('Por favor, complete todos los campos obligatorios.', 'error')
            return render_template('teacher/task_form.html', courses=teacher_courses, task=task, 
                                   action=url_for('teacher.edit_task', task_id=task_id))

        update_data = {
            'course_id': ObjectId(course_id),
            'title': title,
            'description': description,
            'due_date': due_date_str,
        }

        try:
            if uploaded_file and uploaded_file.filename != '' :
                if allowed_file(uploaded_file.filename):
                    # A new file is uploaded.
                    # 1. Delete old physical file from server
                    if current_file_path and os.path.exists(os.path.join(current_app.root_path, current_file_path)):
                        try:
                            os.remove(os.path.join(current_app.root_path, current_file_path))
                        except OSError as e:
                            current_app.logger.error(f"Error deleting old task file: {e}")
                    
                    # 2. Soft-delete old InstitutionalFile record
                    if existing_institutional_file_doc:
                        InstitutionalFile.delete(str(existing_institutional_file_doc['_id']))

                    # 3. Save new physical file
                    filename = secure_filename(uploaded_file.filename)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    unique_filename = f"{timestamp}_{filename}"
                    
                    course_task_upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER_TASKS)
                    os.makedirs(course_task_upload_path, exist_ok=True)
                    
                    file_save_path = os.path.join(course_task_upload_path, unique_filename)
                    uploaded_file.save(file_save_path)
                    new_file_path_for_db = os.path.join(UPLOAD_FOLDER_TASKS, unique_filename)

                    # 4. Create new InstitutionalFile record
                    InstitutionalFile.create(
                        title=f"Adjunto: {title}",
                        description=f"Archivo adjunto para la tarea '{title}' (actualizado)",
                        file_path=new_file_path_for_db,
                        file_type=uploaded_file.mimetype,
                        uploaded_by=teacher_id,
                        category='tasks',
                        related_task_id=task_id
                    )
                else:
                    flash('Tipo de archivo no permitido.', 'error')
                    return render_template('teacher/task_form.html', courses=teacher_courses, task=task, 
                                           action=url_for('teacher.edit_task', task_id=task_id))
            
            update_data['file_path'] = new_file_path_for_db # Update task with new or existing path

            if Task.update(task_id, update_data):
                flash('Tarea actualizada exitosamente.', 'success')
                return redirect(url_for('teacher.manage_tasks'))
            else:
                flash('No se pudo actualizar la tarea o no hubo cambios.', 'info')
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            current_app.logger.error(f"Error updating task: {e}")
            flash(f'Error al actualizar la tarea: {e}', 'error')
        
        return render_template('teacher/task_form.html', courses=teacher_courses, task=task, 
                               action=url_for('teacher.edit_task', task_id=task_id))

    task_for_form = dict(task)
    if task_for_form.get('course_id'):
        task_for_form['course_id'] = str(task_for_form['course_id'])
        
    return render_template('teacher/task_form.html', courses=teacher_courses, task=task_for_form, 
                           action=url_for('teacher.edit_task', task_id=task_id))

@teacher.route('/tasks/delete/<task_id>', methods=['POST'])
@login_required
@role_required('teacher')
def delete_task(task_id):
    task = Task.find_by_id(task_id) # This finds active tasks
    if not task:
        # Attempt to find an inactive task if deletion is re-attempted or task was already soft-deleted
        task = Task.collection.find_one({'_id': ObjectId(task_id)}) 
        if not task:
            flash('Tarea no encontrada.', 'error')
            return redirect(url_for('teacher.manage_tasks'))

    if task['teacher_id'] != ObjectId(session.get('user_id')):
        flash('No tienes permiso para eliminar esta tarea.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

    try:
        # Soft delete the task itself
        task_deleted = Task.delete(task_id) 

        # Find and soft-delete the associated InstitutionalFile if it exists
        institutional_file_doc = InstitutionalFile.collection.find_one({
            'related_task_id': ObjectId(task_id),
            # 'active': True # Find even if already marked inactive by some other process
        })

        if institutional_file_doc:
            file_path_to_delete = institutional_file_doc.get('file_path')
            if InstitutionalFile.delete(str(institutional_file_doc['_id'])):
                current_app.logger.info(f"Soft-deleted InstitutionalFile for task {task_id}")
                # Optionally, delete the physical file from server if no other active InstitutionalFile uses it.
                # For simplicity with soft delete, we might leave the physical file or implement a cleanup job.
                # Here, we'll remove the physical file associated with this *task* if its path exists.
                if file_path_to_delete and os.path.exists(os.path.join(current_app.root_path, file_path_to_delete)):
                    try:
                        os.remove(os.path.join(current_app.root_path, file_path_to_delete))
                        current_app.logger.info(f"Successfully deleted physical task file: {file_path_to_delete}")
                    except OSError as e:
                        current_app.logger.error(f"Error deleting physical task file: {e}")
            else:
                current_app.logger.warning(f"Could not soft-delete InstitutionalFile for task {task_id}")
        
        if task_deleted:
            flash('Tarea eliminada exitosamente.', 'success')
        else:
            flash('No se pudo eliminar la tarea (puede que ya estuviera inactiva).', 'warning')
    except Exception as e:
        current_app.logger.error(f"Error deleting task or its associated file: {e}")
        flash(f'Error al eliminar la tarea: {e}', 'error')
    
    return redirect(url_for('teacher.manage_tasks'))

@teacher.route('/tasks/attachment/<task_id>')
@login_required
@role_required('teacher') 
def download_task_attachment(task_id):
    task = Task.find_by_id(task_id) # Finds active tasks
    user_role = session.get('role')
    user_id = session.get('user_id')

    if not task:
        flash('Tarea no encontrada o no activa.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

    # Find the InstitutionalFile associated with this task
    # This is more reliable than just using task['file_path'] if we centralize file metadata
    institutional_file_doc = InstitutionalFile.collection.find_one({
        'related_task_id': ObjectId(task_id),
        'active': True # Ensure the file record itself is active
    })

    if not institutional_file_doc:
        # Fallback: try using the file_path from the task if no specific InstitutionalFile record found
        # This might happen if InstitutionalFile records weren't created for older tasks.
        if task.get('file_path'):
             # Create a temporary file_doc structure for permission check if only task.file_path exists
            institutional_file_doc = {
                'file_path': task.get('file_path'),
                'category': 'tasks', # Assume 'tasks' category
                'active': True,
                'uploaded_by': task.get('teacher_id') # For ownership check
            }
        else:
            flash('Archivo adjunto no encontrado o no disponible.', 'error')
            return redirect(url_for('teacher.manage_tasks'))
    
    # Use the centralized permission check
    if not InstitutionalFile.can_user_access_file(user_role, user_id, institutional_file_doc):
        flash('No tienes permiso para acceder a este archivo.', 'error')
        return redirect(url_for('teacher.manage_tasks'))
        
    file_relative_path = institutional_file_doc.get('file_path')
    if not file_relative_path or not os.path.exists(os.path.join(current_app.root_path, file_relative_path)):
        flash('Archivo físico no encontrado en el servidor.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

    try:
        file_full_path = os.path.join(current_app.root_path, file_relative_path)
        # Try to get a more user-friendly download name
        original_filename_guess = institutional_file_doc.get('title', file_relative_path.split('/')[-1])
        if 'Adjunto:' in original_filename_guess: # Clean up title if it was auto-generated
            original_filename_guess = original_filename_guess.replace(f"Adjunto: {task.get('title')}", '').strip()
            if not original_filename_guess or not '.' in original_filename_guess : # if it results in empty or no extension
                 original_filename_guess = file_relative_path.split('_', 1)[-1] if '_' in file_relative_path else file_relative_path.split('/')[-1]


        return send_file(file_full_path, as_attachment=True, download_name=original_filename_guess)
    except Exception as e:
        current_app.logger.error(f"Error downloading task attachment: {e}")
        flash('Error al descargar el archivo adjunto.', 'error')
        return redirect(url_for('teacher.manage_tasks'))

@teacher.route('/grades', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def manage_grades():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        grade_value = float(request.form.get('grade_value'))
        grade_type = request.form.get('grade_type')
        description = request.form.get('description', '')
        teacher_id = session.get('user_id')

        if all([student_id, course_id, float(grade_value), grade_type]):
            Grade.create(student_id, course_id, teacher_id, float(grade_value), grade_type, description)
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
    teacher_id = session.get('user_id')
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category') # e.g., 'academic', 'general', 'teacher_specific'

        if not title or not description or not category:
            flash('Título, descripción y categoría son obligatorios.', 'error')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo.', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename # Ensure unique filename

            # Determine upload folder based on category or keep it general
            # For now, all teacher-uploaded non-task files go to the main UPLOAD_FOLDER
            upload_path_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            os.makedirs(upload_path_dir, exist_ok=True)

            file_save_path = os.path.join(upload_path_dir, unique_filename)
            file.save(file_save_path)

            file_type = unique_filename.rsplit('.', 1)[1].lower()
            relative_path = os.path.join(UPLOAD_FOLDER, unique_filename)

            file_id = InstitutionalFile.create(
                title, description, relative_path, file_type,
                teacher_id, category 
            )

            if file_id:
                flash('Archivo subido exitosamente.', 'success')
            else:
                flash('Error al guardar el archivo en la base de datos.', 'error')
        else:
            flash('Tipo de archivo no permitido.', 'error')

    # Teachers see files based on their role and ownership
    files = InstitutionalFile.find_all_for_role('teacher', teacher_id)
    return render_template('teacher/files.html', files=files)

#Ruta para descarga de archivos
@teacher.route('/files/download/<file_id_str>')
@login_required
# Role check handled by can_user_access_file
def download_file(file_id_str):
    user_role = session.get('role')
    user_id = session.get('user_id')
    
    try:
        if not ObjectId.is_valid(file_id_str):
            flash('ID de archivo inválido.', 'error')
            return redirect(url_for('teacher.manage_files'))
            
        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})
        
        if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
            flash('Acceso denegado o archivo no encontrado.', 'error')
            return redirect(url_for('teacher.manage_files'))

        file_path_relative = file_doc['file_path']
        file_path_absolute = os.path.join(current_app.root_path, file_path_relative)

        if os.path.exists(file_path_absolute):
            download_name = f"{file_doc.get('title', 'archivo')}.{file_doc.get('file_type', 'bin')}"
            return send_file(file_path_absolute, as_attachment=True, download_name=download_name)
        else:
            flash('Archivo físico no encontrado en el servidor.', 'error')
            # Mark the institutional file as inactive if physical file is missing? Or just log.
            current_app.logger.error(f"Physical file not found: {file_path_absolute} for InstitutionalFile ID: {file_id_str}")
            return redirect(url_for('teacher.manage_files'))

    except Exception as e:
        current_app.logger.error(f"Error downloading file ID {file_id_str}: {e}")
        flash(f'Error al descargar el archivo: {str(e)}', 'error')
        return redirect(url_for('teacher.manage_files'))

@teacher.route('/files/details_json/<file_id_str>')
@login_required
# Role check will be implicitly handled by fetching logic or can be added if direct access needs restriction
def get_file_details_json(file_id_str):
    user_role = session.get('role')
    user_id = session.get('user_id')

    if not ObjectId.is_valid(file_id_str):
        return jsonify({'success': False, 'error': 'Invalid file ID'}), 400

    file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})

    if not file_doc:
        return jsonify({'success': False, 'error': 'File not found'}), 404

    # Basic permission check, can be expanded
    if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Prepare data for JSON response
    file_details = {
        'id': str(file_doc['_id']),
        'title': file_doc.get('title', 'N/A'),
        'description': file_doc.get('description', 'Sin descripción.'),
        'category': file_doc.get('category', 'N/A'),
        'file_type': file_doc.get('file_type', 'N/A'),
        'created_at': file_doc.get('created_at').strftime('%d/%m/%Y %H:%M') if file_doc.get('created_at') else 'N/A',
        'uploaded_by': file_doc.get('uploaded_by'), # Potentially resolve to username later if needed
        'file_path': file_doc.get('file_path') # For admin/debug, not usually shown to all
    }
    # Add uploader username
    if file_doc.get('uploaded_by'):
        uploader = User.find_by_id(file_doc['uploaded_by'])
        file_details['uploader_name'] = f"{uploader.get('first_name', '')} {uploader.get('last_name', '')}".strip() if uploader else 'Desconocido'
    else:
        file_details['uploader_name'] = 'Sistema'


    return jsonify({'success': True, 'file': file_details})

@teacher.route('/my-students')
@login_required
@role_required('teacher')
def my_students():
    teacher_id = session.get('user_id')
    
    # Obtener los cursos del profesor
    courses = Course.find_by_teacher_id(teacher_id)
    
    # Estructura para almacenar estudiantes por curso
    students_by_course = []
    
    for course in courses:
        course_data = {
            'course_info': course,
            'students': []
        }
        
        # Obtener estudiantes matriculados en este curso
        enrolled_students = CourseEnrollment.get_students_by_course(str(course['_id']))
        
        # Para cada estudiante, obtener información adicional
        for student in enrolled_students:
            # Obtener las calificaciones del estudiante en este curso
            grades = list(Grade.collection.find({
                'student_id': student['_id'],
                'course_id': course['_id']
            }))
            
            # Calcular promedio
            grade_values = [float(g['grade_value']) for g in grades if 'grade_value' in g]
            avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0
            
            student_data = {
                'info': student,
                'grades_count': len(grades),
                'average_grade': round(avg_grade, 2)
            }
            course_data['students'].append(student_data)
        
        students_by_course.append(course_data)
    
    return render_template('teacher/my_students.html', students_by_course=students_by_course)

@teacher.route('/my-students/download-list')
@login_required
@role_required('teacher')
def download_students_list():
    teacher_id = session.get('user_id')
    teacher = User.find_by_id(teacher_id)
    courses = Course.find_by_teacher_id(teacher_id)
    
    # Generar HTML para la lista
    students_data = []
    for course in courses:
        enrolled_students = CourseEnrollment.get_students_by_course(str(course['_id']))
        students_data.append({
            'course': course,
            'students': enrolled_students
        })
    
    # Renderizar el HTML
    html = render_template(
        'teacher/students_list.html',
        teacher=teacher,
        students_data=students_data,
        generation_date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    )
    
    # Crear respuesta con el HTML
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename=lista_estudiantes.html'
    
    return response

@teacher.route('/attendance', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def manage_attendance():
    teacher_id = session.get('user_id')
    courses = Course.find_by_teacher_id(teacher_id)
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        date = request.form.get('date')
        attendance_data = request.form.getlist('attendance[]')
        student_ids = request.form.getlist('student_ids[]')
        
        if all([course_id, date, attendance_data, student_ids]):
            # Guardar la asistencia para cada estudiante
            for student_id, is_present in zip(student_ids, attendance_data):
                Attendance.create(
                    student_id=student_id,
                    course_id=course_id,
                    date=datetime.datetime.strptime(date, '%Y-%m-%d'),
                    is_present=(is_present == 'true'),
                    recorded_by=teacher_id
                )
            flash('Asistencia registrada exitosamente', 'success')
        else:
            flash('Por favor complete todos los campos requeridos', 'error')
    
    # Obtener los estudiantes por curso
    students_by_course = []
    for course in courses:
        enrolled_students = CourseEnrollment.get_students_by_course(str(course['_id']))
        students_by_course.append({
            'course': course,
            'students': enrolled_students
        })
    
    return render_template('teacher/attendance.html', 
                         students_by_course=students_by_course,
                         today=datetime.datetime.now().strftime('%Y-%m-%d'))

@teacher.route('/attendance/export/<course_id>/<date>')
@login_required
@role_required('teacher')
def export_attendance(course_id, date):
    teacher_id = session.get('user_id')
    course = Course.find_by_id(course_id)
    
    if not course:
        flash('Curso no encontrado', 'error')
        return redirect(url_for('teacher.manage_attendance'))
    
    # Obtener la asistencia del día especificado
    attendance_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    attendance_records = Attendance.find_by_course_and_date(course_id, attendance_date)
    
    # Obtener todos los estudiantes del curso
    enrolled_students = CourseEnrollment.get_students_by_course(course_id)
    
    # Crear un diccionario de asistencia por estudiante
    attendance_by_student = {str(record['student_id']): record['is_present'] 
                           for record in attendance_records}
    
    # Renderizar el template HTML
    html = render_template(
        'teacher/attendance_report.html',
        course=course,
        students=enrolled_students,
        attendance=attendance_by_student,
        date=attendance_date.strftime('%d/%m/%Y'),
        teacher_name=f"{session.get('first_name')} {session.get('last_name')}"
    )
    
    # Crear respuesta con el HTML
    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=asistencia_{course["name"]}_{date}.html'
    
    return response

@teacher.route('/schedule')
@login_required
@role_required('teacher')
def schedule():
    teacher_id = session.get('user_id')
    courses = Course.find_by_teacher_id(teacher_id)
    
    # Aquí podrías obtener los horarios reales de una colección de horarios
    # Por ahora usaremos datos de ejemplo
    schedule_data = {
        'Monday': [
            {'time': '08:00 - 09:30', 'course': 'Matemáticas 3A'},
            {'time': '09:45 - 11:15', 'course': 'Álgebra 5B'}
        ],
        'Tuesday': [
            {'time': '08:00 - 09:30', 'course': 'Matemáticas 3A'},
            {'time': '09:45 - 11:15', 'course': 'Geometría 4A'}
        ],
        # ... más días
    }
    
    return render_template('teacher/schedule.html', schedule=schedule_data, courses=courses)

@teacher.route('/reports')
@login_required
@role_required('teacher')
def reports():
    teacher_id = session.get('user_id')
    courses = Course.find_by_teacher_id(teacher_id)
    
    # Obtener estadísticas generales
    total_students = 0
    total_grades = 0
    overall_average = 0
    course_stats = []
    
    for course in courses:
        students = CourseEnrollment.get_students_by_course(str(course['_id']))
        grades = list(Grade.collection.find({'course_id': course['_id']}))
        
        grade_values = [float(g['grade_value']) for g in grades if 'grade_value' in g]
        avg_grade = sum(grade_values) / len(grade_values) if grade_values else 0
        
        total_students += len(students)
        total_grades += len(grades)
        
        course_stats.append({
            'name': course['name'],
            'students_count': len(students),
            'average_grade': round(avg_grade, 2),
            'attendance_rate': '95%'  # Esto se podría calcular desde la colección de asistencia
        })
    
    if total_grades > 0:
        overall_average = total_grades / len(courses)
    
    stats = {
        'total_students': total_students,
        'total_courses': len(courses),
        'overall_average': round(overall_average, 2),
        'course_stats': course_stats
    }
    
    return render_template('teacher/reports.html', stats=stats)
