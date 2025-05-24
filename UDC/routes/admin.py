from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify  
from models import Event, User, InstitutionalInfo, InstitutionalFile, StudentParentRelation # Asegúrate de que StudentParentRelation esté aquí  
import os  
from bson import ObjectId  
from werkzeug.utils import secure_filename  
from flask import current_app  
import datetime  
from routes.auth import admin_required
from flask import send_file

  
admin = Blueprint('admin', __name__)  

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
  
@admin.route('/events/add', methods=['GET', 'POST'])  
@admin_required  
def add_event():  
    if request.method == 'POST':  
        title = request.form.get('title')  
        date = request.form.get('date')  
        time = request.form.get('time')  
        location = request.form.get('location')  
        description = request.form.get('description')  
          
        if title and date and time and location and description:  
            event_id = Event.create(title, date, time, location, description)  
            if event_id:  
                flash('Evento creado exitosamente', 'success')  
                return redirect(url_for('admin.events'))  
            else:  
                flash('Error al crear el evento', 'error')  
        else:  
            flash('Todos los campos son obligatorios', 'error')  
      
    return render_template('admin/event_form.html')  
  
@admin.route('/events/edit/<event_id>', methods=['GET', 'POST'])  
@admin_required  
def edit_event(event_id):  
    event = Event.find_by_id(event_id)  
      
    if not event:  
        flash('Evento no encontrado', 'error')  
        return redirect(url_for('admin.events'))  
      
    if request.method == 'POST':  
        title = request.form.get('title')  
        date = request.form.get('date')  
        time = request.form.get('time')  
        location = request.form.get('location')  
        description = request.form.get('description')  
          
        if title and date and time and location and description:  
            if Event.update(event_id, title, date, time, location, description):  
                flash('Evento actualizado exitosamente', 'success')  
                return redirect(url_for('admin.events'))  
            else:  
                flash('Error al actualizar el evento', 'error')  
        else:  
            flash('Todos los campos son obligatorios', 'error')  
      
    return render_template('admin/event_form.html', event=event)  
@admin.route('/events/add-ajax', methods=['POST'])  
@admin_required  
def add_event_ajax():  
    try:  
        # Usar los nombres que están llegando desde el JavaScript
        title = request.form.get('eventTitle')  
        date = request.form.get('eventDate')  
        time = request.form.get('eventTime')  
        location = request.form.get('eventLocation')  
        description = request.form.get('eventDescription')  
        
        if title and date and time and location and description:  
            event_id = Event.create(title, date, time, location, description)  
            if event_id:  
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
                return jsonify({'success': False, 'message': 'Error al crear el evento'})  
        else:  
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})  
    except Exception as e:  
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
@admin.route('/events/delete/<event_id>')  
@admin_required  
def delete_event(event_id):  
    if Event.delete(event_id):  
        flash('Evento eliminado exitosamente', 'success')  
    else:  
        flash('Error al eliminar el evento', 'error')  
      
    return redirect(url_for('admin.events'))

@admin.route('/files')  
@admin_required  
def files():  
    files = InstitutionalFile.find_all()  
    return render_template('admin/files.html', files=files)  
  
@admin.route('/files/add', methods=['GET', 'POST'])  
@admin_required  
def add_file():  
    if request.method == 'POST':  
        try:  
            title = request.form.get('title')  
            description = request.form.get('description')  
            category = request.form.get('category')  
              
            # Validaciones  
            if not title or not description:  
                flash('Título y descripción son obligatorios', 'error')  
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

@admin.route('/files/download/<file_id>')  
@admin_required  
def download_file(file_id):  
    try:  
        file_doc = InstitutionalFile.collection.find_one({'_id': ObjectId(file_id)})  
        if not file_doc:  
            flash('Archivo no encontrado', 'error')  
            return redirect(url_for('admin.files'))  
          
        file_path = os.path.join(current_app.root_path, file_doc['file_path'])  
          
        if os.path.exists(file_path):  
            return send_file(file_path, as_attachment=True,   
                           download_name=f"{file_doc['title']}.{file_doc['file_type']}")  
        else:  
            flash('Archivo físico no encontrado', 'error')  
            return redirect(url_for('admin.files'))  
              
    except Exception as e:  
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