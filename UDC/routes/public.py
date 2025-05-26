from flask import Blueprint, render_template, current_app, send_file, flash, redirect, url_for, session, jsonify
from models import Event, InstitutionalFile
from bson import ObjectId
import os
from config import Config
from dotenv import load_dotenv
from flask import session  
from models import User, InstitutionalFile  
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
    try:  
        # Verificar si hay un usuario autenticado y obtener su rol  
        user_role = 'public'  # Por defecto público  
        if 'user_id' in session:  
            from models import User  
            user = User.find_by_id(session['user_id'])  
            if user:  
                user_role = user.get('role', 'public')  
          
        files = InstitutionalFile.find_all_for_role(user_role)  
        print(f"DEBUG: Archivos obtenidos para rol '{user_role}': {len(files)}")  
          
        # Procesar archivos para asegurar que tengan todos los campos necesarios  
        processed_files = []  
        for file_data in files:  
            # Si file_data es un diccionario de MongoDB  
            if isinstance(file_data, dict):  
                processed_file = {  
                    'id': str(file_data.get('_id', '')),  
                    'name': file_data.get('title', 'Sin título'),  # Cambiar 'title' por 'name'  
                    'title': file_data.get('title', 'Sin título'),  
                    'description': file_data.get('description', 'Sin descripción'),  
                    'category': file_data.get('category', 'general'),  
                    'file_type': file_data.get('file_type', 'N/A'),  
                    'file_path': file_data.get('file_path', ''),  
                    'created_at': file_data.get('created_at'),  
                    'updated_at': file_data.get('updated_at'),  
                    'uploader_name': file_data.get('uploader_name', 'Sistema')  
                }  
            else:  
                # Si es un objeto con atributos  
                processed_file = {  
                    'id': str(getattr(file_data, '_id', getattr(file_data, 'id', ''))),  
                    'name': getattr(file_data, 'title', 'Sin título'),  # Cambiar 'title' por 'name'  
                    'title': getattr(file_data, 'title', 'Sin título'),  
                    'description': getattr(file_data, 'description', 'Sin descripción'),  
                    'category': getattr(file_data, 'category', 'general'),  
                    'file_type': getattr(file_data, 'file_type', 'N/A'),  
                    'file_path': getattr(file_data, 'file_path', ''),  
                    'created_at': getattr(file_data, 'created_at', None),  
                    'updated_at': getattr(file_data, 'updated_at', None),  
                    'uploader_name': getattr(file_data, 'uploader_name', 'Sistema')  
                }  
              
            processed_files.append(processed_file)  
              
        return render_template('public/general_files.html', files=processed_files, title="Documentos Generales")  
    except Exception as e:  
        print(f"Error en view_general_files: {e}")  
        flash('Error al cargar los documentos.', 'error')  
        return render_template('public/general_files.html', files=[], title="Documentos Generales")
@public.route('/files/download/<file_id_str>')    
def download_general_file(file_id_str):    
    if not ObjectId.is_valid(file_id_str):    
        flash('ID de archivo inválido.', 'error')    
        return redirect(url_for('public.view_general_files'))    
  
    # Verificar rol del usuario  
    user_role = 'public'  
    user_id = None  
    if 'user_id' in session:  
        from models import User  
        user = User.find_by_id(session['user_id'])  
        if user:  
            user_role = user.get('role', 'public')  
            user_id = session['user_id']  
  
    # Buscar el archivo  
    file_doc = InstitutionalFile.collection.find_one({  
        '_id': ObjectId(file_id_str),  
        'active': True  
    })  
  
    if not file_doc:  
        flash('Archivo no encontrado.', 'error')  
        return redirect(url_for('public.view_general_files'))  
  
    # Verificar permisos usando el sistema de roles  
    if not InstitutionalFile.can_user_access_file(user_role, user_id, file_doc):  
        flash('No tienes permiso para acceder a este archivo.', 'error')  
        return redirect(url_for('public.view_general_files'))  
  
    # Usar el mismo patrón que otros endpoints  
    file_path_relative = file_doc['file_path']  
    file_path_absolute = os.path.join(current_app.root_path, file_path_relative)  
      
    if not os.path.exists(file_path_absolute):    
        flash('El archivo físico no fue encontrado en el servidor.', 'error')    
        return redirect(url_for('public.view_general_files'))    
      
    try:    
        download_name = f"{file_doc.get('title', 'archivo')}.{file_doc.get('file_type', 'bin')}"  
        return send_file(file_path_absolute, as_attachment=True, download_name=download_name)  
    except Exception as e:    
        current_app.logger.error(f"Error sending file {file_id_str} for download: {e}")    
        flash('Error al descargar el archivo.', 'error')    
        return redirect(url_for('public.view_general_files'))
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


# Endpoint para vista previa  
@public.route('/files/preview/<file_id_str>')  
def preview_file(file_id_str):  
    if not ObjectId.is_valid(file_id_str):  
        return "ID de archivo inválido", 400  
      
    # Verificar rol del usuario  
    user_role = 'public'  
    if 'user_id' in session:  
        user = User.find_by_id(session['user_id'])  
        if user:  
            user_role = user.get('role', 'public')  
      
    # Buscar el archivo según el rol  
    if user_role == 'public':  
        file_doc = InstitutionalFile.collection.find_one({  
            '_id': ObjectId(file_id_str),  
            'active': True,  
            'category': 'general'  
        })  
    else:  
        files = InstitutionalFile.find_all_for_role(user_role)  
        file_doc = next((f for f in files if str(f.get('_id')) == file_id_str), None)  
      
    if not file_doc:  
        return "Archivo no encontrado", 404  
      
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_INSTITUTIONAL'], file_doc['file_path'])  
    if not os.path.exists(file_path):  
        return "Archivo no encontrado en el servidor", 404  
      
    try:  
        # Determinar el tipo MIME basado en la extensión  
        import mimetypes  
        mimetype, _ = mimetypes.guess_type(file_path)  
          
        # Para PDFs y otros documentos que se pueden mostrar en iframe  
        if mimetype in ['application/pdf', 'text/plain', 'text/html']:  
            return send_file(file_path,   
                           as_attachment=False,   
                           mimetype=mimetype,  
                           download_name=file_doc.get('title', 'archivo'))  
          
        # Para imágenes  
        elif mimetype and mimetype.startswith('image/'):  
            return send_file(file_path,   
                           as_attachment=False,   
                           mimetype=mimetype)  
          
        # Para otros tipos de archivo, mostrar mensaje informativo  
        else:  
            return f"""  
            <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">  
                <h3>Vista previa no disponible</h3>  
                <p>El archivo "{file_doc.get('title', 'Sin título')}" no se puede previsualizar en el navegador.</p>  
                <p>Tipo de archivo: {file_doc.get('file_type', 'Desconocido')}</p>  
                <p><a href="{url_for('public.download_general_file', file_id_str=file_id_str)}"   
                      style="color: #007bff; text-decoration: none;">  
                      Descargar archivo  
                   </a></p>  
            </div>  
            """, 200, {'Content-Type': 'text/html'}  
              
    except Exception as e:  
        return f"""  
        <div style="padding: 20px; text-align: center; font-family: Arial, sans-serif;">  
            <h3>Error al cargar vista previa</h3>  
            <p>No se pudo cargar la vista previa del archivo.</p>  
            <p>Error: {str(e)}</p>  
        </div>  
        """, 500, {'Content-Type': 'text/html'}