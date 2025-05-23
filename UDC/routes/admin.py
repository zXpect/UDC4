from flask import Blueprint, render_template, request, redirect, url_for, flash,session,jsonify
from models import Event  
from routes.auth import admin_required  
from models import User
from models import InstitutionalInfo
from models import InstitutionalFile

  
admin = Blueprint('admin', __name__)  
  
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
        title = request.form.get('title')  
        description = request.form.get('description')  
        category = request.form.get('category')  
        # Lógica de subida de archivos aquí  
        file_path = '/uploads/placeholder.pdf'  
          
        if title and description:  
            InstitutionalFile.create(title, description, file_path, 'pdf', session.get('user_id'), category)  
            flash('Archivo subido exitosamente', 'success')  
            return redirect(url_for('admin.files'))  
      
    return render_template('admin/file_form.html')  
  
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