import os  
import magic  
from werkzeug.utils import secure_filename  
from config import Config

def validate_file_security(file):  
    """Validar seguridad del archivo"""  
    if not file or file.filename == '':  
        return False, "No se seleccionó archivo"  
      
    # Validar extensión  
    if not allowed_file(file.filename):  
        return False, "Tipo de archivo no permitido"  
      
    # Validar tamaño  
    file.seek(0, os.SEEK_END)  
    size = file.tell()  
    file.seek(0)  
      
    if size > 16 * 1024 * 1024:  # 16MB  
        return False, "Archivo demasiado grande (máx. 16MB)"  
      
    # Validar tipo MIME  
    try:  
        mime_type = magic.from_buffer(file.read(1024), mime=True)  
        file.seek(0)  
          
        allowed_mimes = {  
            'application/pdf', 'image/jpeg', 'image/png', 'image/gif',  
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  
            'text/plain'  
        }  
          
        if mime_type not in allowed_mimes:  
            return False, f"Tipo de archivo no seguro: {mime_type}"  
              
    except Exception:  
        return False, "No se pudo verificar el tipo de archivo"  
      
    return True, "Archivo válido"  
  
def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS