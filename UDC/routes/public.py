from flask import Blueprint, render_template, current_app, send_file, flash, redirect, url_for, session, jsonify
from models import Event, InstitutionalFile
from bson import ObjectId
import os
from config import Config
from dotenv import load_dotenv
load_dotenv()
  
public = Blueprint('public', __name__)  
  
@public.route('/')  
def index():  
    try:
        events = Event.find_all()[:3]  
    except Exception as e:
        print("Error al conectar con Mongo:",e)
        events=[]
    return render_template('index.html', events=events)  
  
@public.route('/about')  
def about():  
    return render_template('public/about.html')  
  
@public.route('/events')  
def events():  
    try:
        events = Event.find_all()
    except Exception as e:
        print("Error al conectar con Mongo:", e)
        events = []
    return render_template('public/events.html', events=events)  
  
@public.route('/contact')  
def contact():  
    return render_template('public/contact.html',   
                         google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)  
  
@public.route('/academic-info')  
def academic_info():  
    return render_template('public/academic_info.html')  
  
@public.route('/general-files')  
def view_general_files():  
    files = InstitutionalFile.find_all_for_role('public')  
    return render_template('public/general_files.html', files=files, title="Documentos Generales")  
  
@public.route('/files/download/<file_id_str>')  
def download_general_file(file_id_str):  
    # Public users can only download 'general' category files  
    if not ObjectId.is_valid(file_id_str):  
        flash('ID de archivo inválido.', 'error')  
        return redirect(url_for('public.general_files_list'))  
  
    file_doc = InstitutionalFile.collection.find_one({  
        '_id': ObjectId(file_id_str),  
        'active': True,  
        'category': 'general'  
    })  
  
    if not file_doc:  
        flash('Archivo no encontrado o no autorizado.', 'error')  
        return redirect(url_for('public.general_files_list'))  
  
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_INSTITUTIONAL'], file_doc['file_path'])  
    if not os.path.exists(file_path):  
        flash('El archivo físico no fue encontrado en el servidor.', 'error')  
        return redirect(url_for('public.general_files_list'))  
    
    try:  
        return send_file(file_path, as_attachment=True, download_name=file_doc['title'] + os.path.splitext(file_doc['file_path'])[1])  
    except Exception as e:  
        current_app.logger.error(f"Error sending file {file_id_str} for public download: {e}")  
        flash('Error al descargar el archivo.', 'error')  
        return redirect(url_for('public.general_files_list'))  
  
@public.route('/files/details_json/<file_id_str>')  
def get_public_file_details_json(file_id_str):  
    if not ObjectId.is_valid(file_id_str):  
        return jsonify({'success': False, 'error': 'ID de archivo inválido'}), 400  
  
    file_doc = InstitutionalFile.collection.find_one({  
        '_id': ObjectId(file_id_str),  
        'active': True,  
        'category': 'general' # Public only sees general  
    })  
  
    if not file_doc:  
        return jsonify({'success': False, 'error': 'Archivo no encontrado o no autorizado'}), 404  
  
    file_details = {  
        'id': str(file_doc['_id']),  
        'title': file_doc.get('title', 'N/A'),  
        'description': file_doc.get('description', 'Sin descripción.'),  
        'category': file_doc.get('category', 'N/A'), # Should always be general  
        'file_type': file_doc.get('file_type', 'N/A'),  
        'created_at': file_doc.get('created_at').strftime('%d/%m/%Y %H:%M') if file_doc.get('created_at') else 'N/A',  
    }  
    # Uploader info might be sensitive for public view, decide if needed  
    # For now, let's omit uploader details for public files.

    return jsonify({'success': True, 'file': file_details})