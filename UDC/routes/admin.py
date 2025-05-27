from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify  
from models import Event, User, InstitutionalInfo, InstitutionalFile, StudentParentRelation, Course, CourseEnrollment 
import os  
from bson import ObjectId  
from werkzeug.utils import secure_filename  
from flask import current_app  
import datetime  
from routes.auth import admin_required
from flask import send_file
import bcrypt
import re  
from datetime import datetime, date 

  
admin = Blueprint('admin', __name__)  
# aver si va
# Configuración para archivos  
UPLOAD_FOLDER = 'uploads'  
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}  

def allowed_file(filename):  
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 
  
@admin.route('/')  
@admin_required  
def dashboard():  
    events = Event.find_all()  
    users_count = User.count_users()  
    events_count = len(events)  
      
    stats = {  
        'events_count': events_count,  
        'users_count': users_count,  
        'files_count': 5  # Placeholder por ahora  
    }  
      
    return render_template('admin/dashboard.html', events=events, stats=stats)


  
@admin.route('/events')  
@admin_required  
def events():  
    events = Event.find_all()  
    return render_template('admin/events.html', events=events)  

def validate_event_data(title, date_str, time_str, location, description):  
    #Validar datos del evento
    errors = []  
      
    # Validar título  
    if not title or len(title.strip()) < 3:  
        errors.append("El título debe tener al menos 3 caracteres")  
    elif len(title) > 100:  
        errors.append("El título no puede exceder 100 caracteres")  
      
    # Validar fecha  
    try:  
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()  
        if event_date < date.today():  
            errors.append("La fecha del evento no puede ser anterior a hoy")  
    except ValueError:  
        errors.append("Formato de fecha inválido")  
      
    # Validar hora  
    try:  
        datetime.strptime(time_str, '%H:%M')  
    except ValueError:  
        errors.append("Formato de hora inválido")  
      
    # Validar ubicación  
    if not location or len(location.strip()) < 3:  
        errors.append("La ubicación debe tener al menos 3 caracteres")  
    elif len(location) > 100:  
        errors.append("La ubicación no puede exceder 100 caracteres")  
      
    # Validar descripción  
    if not description or len(description.strip()) < 10:  
        errors.append("La descripción debe tener al menos 10 caracteres")  
    elif len(description) > 500:  
        errors.append("La descripción no puede exceder 500 caracteres")  
      
    return errors  

@admin.route('/events/add', methods=['GET', 'POST'])  
@admin_required  
def add_event():  
    if request.method == 'POST': 
        try: 
            title = request.form.get('title', '').strip()   
            date = request.form.get('date', '').strip()    
            time = request.form.get('time', '').strip()   
            location = request.form.get('location', '').strip()    
            description = request.form.get('description', '').strip()    
            
            errors = validate_event_data(title, date, time, location, description)

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/event_form.html')
            
            event_id = Event.create(title, date, time, location, description)  
            if event_id:  
                flash('Evento creado exitosamente', 'success')  
                return redirect(url_for('admin.events'))  
            else:  
                flash('Error al crear el evento', 'error')  
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')  
    else:  
        flash('Ingresaste correctamente, recuerda rellenar todos los campos', 'success')
      
    return render_template('admin/event_form.html')  
  
@admin.route('/events/edit/<event_id>', methods=['GET', 'POST'])  
@admin_required  
def edit_event(event_id):  
    event = Event.find_by_id(event_id)  
      
    if not event:  
        flash('Evento no encontrado', 'error')  
        return redirect(url_for('admin.dashboard')) # Redirect to dashboard if not found
      
    if request.method == 'POST':  
        try:
            title = request.form.get('title', '').strip()  
            date = request.form.get('date', '').strip()  
            time = request.form.get('time', '').strip()  
            location = request.form.get('location', '').strip()  
            description = request.form.get('description', '').strip()  
            
            errors = validate_event_data(title, date, time, location, description)
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/event_form.html', event=event)

            if Event.update(event_id, title, date, time, location, description):
                flash('Evento actualizado exitosamente', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Error al actualizar el evento', 'error')
                return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')
            return redirect(url_for('admin.dashboard'))
      
    # For GET request, or if POST had issues and we want to show the separate form page:
    return render_template('admin/event_form.html', event=event)  

@admin.route('/events/add-ajax', methods=['POST'])  
@admin_required  
def add_event_ajax():  
    try:  
        # Usar los nombres que están llegando desde el JavaScript
        title = request.form.get('eventTitle', '').strip()    
        date = request.form.get('eventDate', '').strip()    
        time = request.form.get('eventTime', '').strip()    
        location = request.form.get('eventLocation', '').strip()    
        description = request.form.get('eventDescription', '').strip()    
        
        errors = validate_event_data(title, date, time, location, description)  
        if errors:  
            return jsonify({'success': False, 'message': errors[0]})  
        
        event_id = Event.create(title, date, time, location, description)  
        if event_id:  
            flash('Evento creado exitosamente desde el modal.', 'success')  
            return jsonify({  
                'success': True,  
                'message': 'Evento creado exitosamente',  
                'event': {  
                    'id': str(event_id),  
                    'title': title,  
                    'date': date,  
                    'time': time,  
                    'location': location,  
                    'description': description  
                }  
            })  
        else:  
            flash('Error al crear el evento desde el modal.', 'error')  
            return jsonify({'success': False, 'message': 'Error al crear el evento'}) 
         
    except Exception as e:  
        flash(f'Error inesperado al crear evento desde modal: {str(e)}', 'error')  
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@admin.route('/events/add-from-dashboard', methods=['POST'])
@admin_required
def add_event_from_dashboard_modal():
    try:
        title = request.form.get('eventTitle', '').strip()
        date = request.form.get('eventDate', '').strip()
        time = request.form.get('eventTime', '').strip()
        location = request.form.get('eventLocation', '').strip()
        description = request.form.get('eventDescription', '').strip()

        errors = validate_event_data(title, date, time, location, description)
        if errors:
            for error in errors:  
                    flash(error, 'error')  
            return redirect(url_for('admin.dashboard'))
        
        event_id = Event.create(title, date, time, location, description)
        if event_id:
            flash('Evento creado exitosamente desde el modal del dashboard.', 'success')
        else:
            flash('Error al crear el evento desde el modal del dashboard.', 'error')
        
    except Exception as e:
        flash(f'Error inesperado al crear evento: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin.route('/events/edit-modal/<event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event_modal(event_id):
    # Validar que el ID sea válido
    if not ObjectId.is_valid(event_id):
        flash('ID de evento inválido.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Buscar el evento
    event = Event.find_by_id(event_id)
    if not event:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            date = request.form.get('date', '').strip()
            time = request.form.get('time', '').strip()
            location = request.form.get('location', '').strip()
            description = request.form.get('description', '').strip()

            # Validar que todos los campos estén presentes
            errors = validate_event_data(title, date, time, location, description)
            if errors:
                for error in errors:  
                    flash(error, 'error')  
                return redirect(url_for('admin.dashboard'))

            if Event.update(event_id, title, date, time, location, description):
                flash('Evento actualizado exitosamente desde el modal.', 'success')
            else:
                flash('Error al actualizar el evento.', 'error')

        except Exception as e:
            current_app.logger.error(f"Error updating event from modal: {str(e)}")
            flash(f'Error al actualizar el evento: {str(e)}', 'error')

        return redirect(url_for('admin.dashboard'))
    
    # Si es GET, renderizar el dashboard con el evento seleccionado para edición
    # (esto sería útil si quisieras mostrar el modal abierto con los datos)
    events = Event.find_all()  
    users_count = User.count_users()  
    events_count = len(events)  
      
    stats = {  
        'events_count': events_count,  
        'users_count': users_count,  
        'files_count': 5  
    }
    
    return render_template('admin/dashboard.html', 
                         events=events, 
                         stats=stats, 
                         edit_event=event)  # Pasar el evento a editar
@admin.route('/events/delete/<event_id>')  
@admin_required  
def delete_event(event_id):  
    current_app.logger.info(f"--- Admin: Attempting to delete event with ID: {event_id} ---") # DIAGNOSTIC LOGGING
    
    # Validar que el ID sea válido
    if not ObjectId.is_valid(event_id):
        current_app.logger.error(f"Invalid event ID format: {event_id}")
        flash('ID de evento inválido.', 'error')
        return redirect(url_for('admin.dashboard'))
        
    try:
        # Intentar encontrar el evento primero
        event = Event.find_by_id(event_id)
        if not event:
            current_app.logger.error(f"Event not found with ID: {event_id}")
            flash('Evento no encontrado en la base de datos.', 'error')
            return redirect(url_for('admin.dashboard'))
            
        # Intentar eliminar el evento
        if Event.delete(event_id):  
            current_app.logger.info(f"Successfully deleted event with ID: {event_id}")
            flash('Evento eliminado exitosamente', 'success')  
        else:  
            current_app.logger.error(f"Failed to delete event with ID: {event_id}")
            flash('Error al eliminar el evento.', 'error') 
    except Exception as e:
        current_app.logger.error(f"Exception during event deletion {event_id}: {str(e)}")
        flash(f'Error al procesar la eliminación: {str(e)}', 'error')
      
    return redirect(url_for('admin.dashboard'))

@admin.route('/files')  
@admin_required  
def files():  
    # Admins see all files (including inactive if find_all_for_role('admin') is designed that way)
    # or all active files if find_all_for_role defaults to active ones.
    # The current implementation of find_all_for_role('admin') fetches ALL files.
    files = InstitutionalFile.find_all_for_role('admin')  
    return render_template('admin/files.html', files=files)  
  
@admin.route('/files/add', methods=['GET', 'POST'])  
@admin_required  
def add_file():  
    if request.method == 'POST':  
        try:  
            title = request.form.get('title')  
            description = request.form.get('description')  
            category = request.form.get('category') # Can be 'general', 'academic', 'administrative', 'tasks' etc.
              
            if not title or not description or not category:  
                flash('Título, descripción y categoría son obligatorios', 'error')  
                return render_template('admin/file_form.html')  
              
            # Verificar si se subió un archivo  
            if 'file' not in request.files:  
                flash('No se seleccionó ningún archivo', 'error')  
                return render_template('admin/file_form.html')  
              
            file = request.files['file']  
              
            if file.filename == '':  
                flash('No se seleccionó ningún archivo', 'error')  
                return render_template('admin/file_form.html')  
              
            if file and allowed_file(file.filename):  
                # Crear directorio si no existe  
                upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)  
                if not os.path.exists(upload_path):  
                    os.makedirs(upload_path)  
                  
                # Generar nombre seguro  
                filename = secure_filename(file.filename)  
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')  
                filename = timestamp + filename  
                  
                file_path = os.path.join(upload_path, filename)  
                file.save(file_path)  
                  
                # Guardar en base de datos  
                file_type = filename.rsplit('.', 1)[1].lower()  
                relative_path = os.path.join(UPLOAD_FOLDER, filename)  
                  
                file_id = InstitutionalFile.create(  
                    title, description, relative_path, file_type,   
                    session.get('user_id'), category  
                )  
                  
                if file_id:  
                    flash('Archivo subido exitosamente', 'success')  
                    return redirect(url_for('admin.files'))  
                else:  
                    flash('Error al guardar el archivo en la base de datos', 'error')  
            else:  
                flash('Tipo de archivo no permitido', 'error')  
                  
        except Exception as e:  
            flash(f'Error al subir el archivo: {str(e)}', 'error')  
      
    return render_template('admin/file_form.html')    

# Agregar ruta para eliminar archivos  
@admin.route('/files/delete/<file_id>')  
@admin_required  
def delete_file(file_id):  
    try:  
        if InstitutionalFile.delete(file_id):  
            flash('Archivo eliminado exitosamente', 'success')  
        else:  
            flash('Error al eliminar el archivo', 'error')  
    except Exception as e:  
        flash(f'Error: {str(e)}', 'error')  
      
    return redirect(url_for('admin.files'))

@admin.route('/files/download/<file_id_str>')  
@admin_required  
def download_file(file_id_str):  
    user_role = session.get('role') # Should be 'admin'
    user_id = session.get('user_id') # Admin's user ID
    try:  
        if not ObjectId.is_valid(file_id_str):
            flash('ID de archivo inválido.', 'error')
            return redirect(url_for('admin.files'))

        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id_str)})  
        
        # Admin should always be able to access, but good practice to use the check
        if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):
            # This case should ideally not be hit for an admin if can_user_access_file is correct for 'admin' role
            # and file_doc exists.
            flash('Acceso denegado o archivo no encontrado.', 'error')  
            return redirect(url_for('admin.files'))  
          
        file_path_relative = file_doc['file_path']
        file_path_absolute = os.path.join(current_app.root_path, file_path_relative)  
          
        if os.path.exists(file_path_absolute):  
            download_name = f"{file_doc.get('title', 'archivo')}.{file_doc.get('file_type', 'bin')}"
            return send_file(file_path_absolute, as_attachment=True,   
                           download_name=download_name)  
        else:  
            flash('Archivo físico no encontrado en el servidor.', 'error')  
            current_app.logger.error(f"Physical file not found: {file_path_absolute} for InstitutionalFile ID: {file_id_str}")
            return redirect(url_for('admin.files'))  
              
    except Exception as e:  
        current_app.logger.error(f"Error admin downloading file ID {file_id_str}: {e}")
        flash(f'Error al descargar: {str(e)}', 'error')  
        return redirect(url_for('admin.files'))  
  
# Ruta pública para descarga (para otros roles)  

@admin.route('/institutional-info', methods=['GET', 'POST'])  
@admin_required  
def institutional_info():  
    if request.method == 'POST':  
        key = request.form.get('key')  
        value = request.form.get('value')  
  
        if key and value:  
            InstitutionalInfo.update_info(key, value, session.get('user_id'))  
            flash('Información actualizada exitosamente', 'success')  
  
    info_list = InstitutionalInfo.get_all_info()  
    return render_template('admin/institutional_info.html', info_list=info_list)  
  
  
@admin.route('/users')  
@admin_required  
def users():  
    users = User.collection.find({'active': True})  
    return render_template('admin/users.html', users=users)  

@admin.route('/students')
@admin_required
def students():
    student_users = list(User.collection.find({'role': 'student', 'active': True}))
    return render_template('admin/students.html', students=student_users)

@admin.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            # Pass back form data to repopulate
            return render_template('admin/user_form.html', user={}, action='add', role='student', 
                                   form_data=request.form)

        # Validate password strength
        is_valid_password, password_error = User.validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('admin/user_form.html', user={}, action='add', role='student',
                                   form_data=request.form)

        try:
            User.create_user(username, password, email, first_name, last_name, role='student')
            flash('Estudiante creado exitosamente.', 'success')
            return redirect(url_for('admin.students'))
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f'Error al crear estudiante: {e}', 'error')
        # Pass back form data to repopulate if error
        return render_template('admin/user_form.html', user={}, action='add', role='student', 
                               form_data=request.form)
    
    return render_template('admin/user_form.html', user={}, action='add', role='student')

@admin.route('/students/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(user_id):
    student = User.find_by_id(user_id)
    if not student or student.get('role') != 'student':
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        # Password change is optional
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        update_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }

        if password: # If password fields are filled, try to update
            if password != confirm_password:
                flash('Las nuevas contraseñas no coinciden.', 'error')
                # Pass back existing student data and new (but flawed) form data
                student['email'] = email # update student dict with attempted changes for re-render
                student['first_name'] = first_name
                student['last_name'] = last_name
                return render_template('admin/user_form.html', user=student, action='edit', role='student')
            
            is_valid_password, password_error = User.validate_password(password)
            if not is_valid_password:
                flash(password_error, 'error')
                student['email'] = email 
                student['first_name'] = first_name
                student['last_name'] = last_name
                return render_template('admin/user_form.html', user=student, action='edit', role='student')

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_password

        try:
            User.update_user(user_id, update_data)
            flash('Estudiante actualizado exitosamente.', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            flash(f'Error al actualizar estudiante: {e}', 'error')
            # Re-render with existing student data if update fails
            return render_template('admin/user_form.html', user=student, action='edit', role='student')

    return render_template('admin/user_form.html', user=student, action='edit', role='student')

@admin.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    # 1. Carga el documento desde MongoDB
    user = User.find_by_id(user_id)
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('admin.users'))

    # 2. Si es POST, procesa el formulario
    if request.method == 'POST':
        # Campos editables
        email         = request.form.get('email')
        first_name    = request.form.get('first_name')
        last_name     = request.form.get('last_name')
        role          = request.form.get('role')
        active        = True if request.form.get('active') == 'on' else False

        # Opcional: cambio de contraseña
        password      = request.form.get('password')
        confirm_pass  = request.form.get('confirm_password')

        update_data = {
            'email':      email,
            'first_name': first_name,
            'last_name':  last_name,
            'role':       role,
            'active':     active
        }

        if password:
            if password != confirm_pass:
                flash('Las contraseñas no coinciden.', 'error')
                user.update({'email': email, 'first_name': first_name, 'last_name': last_name})
                return render_template('admin/user_form.html',
                                       user=user,
                                       action='edit',
                                       role=user.get('role'))

            is_valid, pwd_err = User.validate_password(password)
            if not is_valid:
                flash(pwd_err, 'error')
                user.update({'email': email, 'first_name': first_name, 'last_name': last_name})
                return render_template('admin/user_form.html',
                                       user=user,
                                       action='edit',
                                       role=user.get('role'))

            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed

        # 3. Guarda los cambios en MongoDB
        try:
            User.update_user(user_id, update_data)
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            flash(f'Error al actualizar usuario: {e}', 'error')
            return render_template('admin/user_form.html',
                                   user=user,
                                   action='edit',
                                   role=user.get('role'))

    # 4. GET: muestra el formulario con datos actuales
    return render_template('admin/edit_user.html',
                           user=user,
                           action='edit',
                           role=user.get('role'))

@admin.route('/students/view/<user_id>')
@admin_required
def view_student(user_id):
    student = User.find_by_id(user_id)
    if not student or student.get('role') != 'student':
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('admin.students'))
    return render_template('admin/user_view.html', user=student, role='student')

@admin.route('/students/delete/<user_id>')
@admin_required
def delete_student(user_id):
    student = User.find_by_id(user_id)
    if not student or student.get('role') != 'student':
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('admin.students'))
    try:
        # Soft delete by setting active to False
        User.update_user(user_id, {'active': False})
        flash('Estudiante eliminado (desactivado) exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar estudiante: {e}', 'error')
    return redirect(url_for('admin.students'))

@admin.route('/teachers')
@admin_required
def teachers():
    teacher_users = list(User.collection.find({'role': 'teacher', 'active': True}))
    return render_template('admin/teachers.html', teachers=teacher_users)

@admin.route('/teachers/add', methods=['GET', 'POST'])
@admin_required
def add_teacher():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('admin/user_form.html', user={}, action='add', role='teacher',
                                   form_data=request.form)
        
        is_valid_password, password_error = User.validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('admin/user_form.html', user={}, action='add', role='teacher',
                                   form_data=request.form)

        try:
            User.create_user(username, password, email, first_name, last_name, role='teacher')
            flash('Profesor creado exitosamente.', 'success')
            return redirect(url_for('admin.teachers'))
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f'Error al crear profesor: {e}', 'error')
        return render_template('admin/user_form.html', user={}, action='add', role='teacher',
                               form_data=request.form)

    return render_template('admin/user_form.html', user={}, action='add', role='teacher')

@admin.route('/teachers/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_teacher(user_id):
    teacher = User.find_by_id(user_id)
    if not teacher or teacher.get('role') != 'teacher':
        flash('Profesor no encontrado.', 'error')
        return redirect(url_for('admin.teachers'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        update_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }

        if password:
            if password != confirm_password:
                flash('Las nuevas contraseñas no coinciden.', 'error')
                teacher['email'] = email
                teacher['first_name'] = first_name
                teacher['last_name'] = last_name
                return render_template('admin/user_form.html', user=teacher, action='edit', role='teacher')
            
            is_valid_password, password_error = User.validate_password(password)
            if not is_valid_password:
                flash(password_error, 'error')
                teacher['email'] = email
                teacher['first_name'] = first_name
                teacher['last_name'] = last_name
                return render_template('admin/user_form.html', user=teacher, action='edit', role='teacher')

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_password

        try:
            User.update_user(user_id, update_data)
            flash('Profesor actualizado exitosamente.', 'success')
            return redirect(url_for('admin.teachers'))
        except Exception as e:
            flash(f'Error al actualizar profesor: {e}', 'error')
            return render_template('admin/user_form.html', user=teacher, action='edit', role='teacher')

    return render_template('admin/user_form.html', user=teacher, action='edit', role='teacher')

@admin.route('/teachers/view/<user_id>')
@admin_required
def view_teacher(user_id):
    teacher = User.find_by_id(user_id)
    if not teacher or teacher.get('role') != 'teacher':
        flash('Profesor no encontrado.', 'error')
        return redirect(url_for('admin.teachers'))
    return render_template('admin/user_view.html', user=teacher, role='teacher')

@admin.route('/teachers/delete/<user_id>')
@admin_required
def delete_teacher(user_id):
    teacher = User.find_by_id(user_id)
    if not teacher or teacher.get('role') != 'teacher':
        flash('Profesor no encontrado.', 'error')
        return redirect(url_for('admin.teachers'))
    try:
        User.update_user(user_id, {'active': False}) # Soft delete
        flash('Profesor eliminado (desactivado) exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar profesor: {e}', 'error')
    return redirect(url_for('admin.teachers'))

@admin.route('/courses')
@admin_required
def courses():
    all_courses_raw = Course.find_all()
    all_courses = []
    for course_data in all_courses_raw:
        teacher_name = "N/A"
        if course_data.get('teacher_id'):
            teacher = User.find_by_id(course_data['teacher_id'])
            if teacher:
                teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
        course_data['teacher_name'] = teacher_name
        all_courses.append(course_data)
    return render_template('admin/courses.html', courses=all_courses)

@admin.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    teachers = list(User.collection.find({'role': 'teacher', 'active': True}))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        teacher_id = request.form.get('teacher_id')
        grade_level = request.form.get('grade_level')

        if not name or not grade_level or not teacher_id:
            flash('Nombre, Nivel y Profesor son campos obligatorios.', 'error')
            return render_template('admin/course_form.html', teachers=teachers, course={})

        try:
            Course.create(name, description, teacher_id, grade_level)
            flash('Curso creado exitosamente.', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            flash(f'Error al crear el curso: {e}', 'error')
    
    return render_template('admin/course_form.html', teachers=teachers, course={}, action='add')

@admin.route('/courses/edit/<course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Course.collection.find_one({'_id': ObjectId(course_id)})
    if not course:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('admin.courses'))

    teachers = list(User.collection.find({'role': 'teacher', 'active': True}))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        teacher_id = request.form.get('teacher_id')
        grade_level = request.form.get('grade_level')

        if not name or not grade_level or not teacher_id:
            flash('Nombre, Nivel y Profesor son campos obligatorios.', 'error')
            # Pass existing course data back to form
            course['name'] = name
            course['description'] = description
            course['teacher_id'] = ObjectId(teacher_id) if teacher_id else None
            course['grade_level'] = grade_level
            return render_template('admin/course_form.html', teachers=teachers, course=course, action='edit')

        update_data = {
            'name': name,
            'description': description,
            'teacher_id': ObjectId(teacher_id) if teacher_id else None,
            'grade_level': grade_level,
            'updated_at': datetime.datetime.utcnow()
        }
        
        try:
            Course.collection.update_one({'_id': ObjectId(course_id)}, {'$set': update_data})
            flash('Curso actualizado exitosamente.', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            flash(f'Error al actualizar el curso: {e}', 'error')

    return render_template('admin/course_form.html', teachers=teachers, course=course, action='edit')

@admin.route('/courses/view/<course_id>')
@admin_required
def view_course(course_id):
    course_data = Course.collection.find_one({'_id': ObjectId(course_id)})
    if not course_data:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('admin.courses'))

    teacher_name = "N/A"
    if course_data.get('teacher_id'):
        teacher = User.find_by_id(course_data['teacher_id'])
        if teacher:
            teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
    course_data['teacher_name'] = teacher_name
    
    return render_template('admin/course_view.html', course=course_data)

@admin.route('/courses/delete/<course_id>')
@admin_required
def delete_course(course_id):
    try:
        result = Course.collection.update_one(
            {'_id': ObjectId(course_id)},
            {'$set': {'active': False, 'updated_at': datetime.datetime.utcnow()}} # Soft delete
        )
        if result.modified_count > 0:
            flash('Curso eliminado (desactivado) exitosamente.', 'success')
        else:
            flash('Curso no encontrado o ya desactivado.', 'error')
    except Exception as e:
        flash(f'Error al eliminar el curso: {e}', 'error')
    return redirect(url_for('admin.courses'))

@admin.route('/courses/<course_id>/enrollments', methods=['GET'])
@admin_required
def manage_course_enrollments(course_id):
    course = Course.collection.find_one({'_id': ObjectId(course_id)})
    if not course:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('admin.courses'))

    enrolled_students_details = CourseEnrollment.get_enrollment_details_for_course(course_id)
    available_students = CourseEnrollment.get_available_students_for_course(course_id)

    # Fetch teacher name for the course view
    teacher_name = "N/A"
    if course.get('teacher_id'):
        teacher = User.find_by_id(course['teacher_id'])
        if teacher:
            teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
    course['teacher_name'] = teacher_name

    return render_template('admin/course_enrollments.html',
                           course=course,
                           enrolled_students=enrolled_students_details,
                           available_students=available_students)

@admin.route('/courses/<course_id>/enroll_student', methods=['POST'])
@admin_required
def enroll_student_in_course(course_id):
    student_id = request.form.get('student_id')
    current_user_id = session.get('user_id') # Assuming admin user ID is in session

    if not student_id:
        flash('Debe seleccionar un estudiante.', 'error')
        return redirect(url_for('admin.manage_course_enrollments', course_id=course_id))

    try:
        CourseEnrollment.enroll_student(course_id, student_id, current_user_id)
        flash('Estudiante inscrito exitosamente.', 'success')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        flash(f'Error al inscribir estudiante: {e}', 'error')
    return redirect(url_for('admin.manage_course_enrollments', course_id=course_id))

@admin.route('/courses/<course_id>/unenroll_student/<student_id>', methods=['POST'])
@admin_required
def unenroll_student_from_course(course_id, student_id):
    try:
        if CourseEnrollment.unenroll_student(course_id, student_id):
            flash('Estudiante desinscrito exitosamente.', 'success')
        else:
            flash('No se pudo desinscribir al estudiante o ya no estaba inscrito.', 'warning')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        flash(f'Error al desinscribir estudiante: {e}', 'error')
    return redirect(url_for('admin.manage_course_enrollments', course_id=course_id))

@admin.route('/link_parent_child', methods=['GET', 'POST'])  
@admin_required  
def link_parent_child():  
    if request.method == 'POST':  
        parent_id = request.form.get('parent_id')  
        student_id = request.form.get('student_id')  
  
        if not parent_id or not student_id:  
            flash('Debe seleccionar un padre y un estudiante.', 'error')  
            return redirect(url_for('admin.link_parent_child'))  
  
        # Verificar si la relación ya existe  
        if StudentParentRelation.verify_parent_child_relationship(parent_id, student_id):  
            flash('Esta relación padre-hijo ya existe.', 'warning')  
            return redirect(url_for('admin.link_parent_child'))  
  
        try:  
            StudentParentRelation.create(student_id, parent_id)  
            flash('Relación padre-hijo creada exitosamente.', 'success')  
        except Exception as e:  
            flash(f'Error al crear la relación: {e}', 'error')  
  
        return redirect(url_for('admin.link_parent_child'))  
  
    # Obtener todos los usuarios con rol 'parent' y 'student'  
    parents = list(User.collection.find({'role': 'parent', 'active': True}))  
    students = list(User.collection.find({'role': 'student', 'active': True}))  
  
    return render_template('admin/link_parent_child.html', parents=parents, students=students)  

@admin.route('/events/edit-from-dashboard', methods=['POST'])
@admin_required
def edit_event_from_dashboard():
    try:
        # Debug: imprimir todos los datos del formulario
        current_app.logger.info(f"Form data received: {dict(request.form)}")
        
        event_id = request.form.get('eventId')
        title = request.form.get('title')
        date = request.form.get('date')
        time = request.form.get('time')
        location = request.form.get('location')
        description = request.form.get('description')

        # Debug: imprimir cada campo individualmente
        current_app.logger.info(f"Event ID: '{event_id}'")
        current_app.logger.info(f"Title: '{title}'")
        current_app.logger.info(f"Date: '{date}'")
        current_app.logger.info(f"Time: '{time}'")
        current_app.logger.info(f"Location: '{location}'")
        current_app.logger.info(f"Description: '{description}'")

        # Verificar si algún campo está vacío o es None
        missing_fields = []
        if not event_id:
            missing_fields.append('eventId')
        if not title:
            missing_fields.append('title')
        if not date:
            missing_fields.append('date')
        if not time:
            missing_fields.append('time')
        if not location:
            missing_fields.append('location')
        if not description:
            missing_fields.append('description')

        if missing_fields:
            current_app.logger.error(f"Missing fields: {missing_fields}")
            flash(f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('admin.dashboard'))

        # Verificar que el event_id sea un ObjectId válido
        if not ObjectId.is_valid(event_id):
            current_app.logger.error(f"Invalid ObjectId: {event_id}")
            flash('ID de evento inválido.', 'error')
            return redirect(url_for('admin.dashboard'))

        # Intentar actualizar el evento
        if Event.update(event_id, title, date, time, location, description):
            current_app.logger.info(f"Event {event_id} updated successfully")
            flash('Evento actualizado exitosamente desde el modal del dashboard.', 'success')
        else:
            current_app.logger.error(f"Failed to update event {event_id}")
            flash('Error al actualizar el evento desde el modal del dashboard.', 'error')

    except Exception as e:
        current_app.logger.error(f"Exception in edit_event_from_dashboard: {str(e)}")
        flash(f'Error al actualizar el evento: {str(e)}', 'error')

    return redirect(url_for('admin.dashboard'))