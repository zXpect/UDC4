import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False

class DevelopmentConfig(Config):
    DEBUG = True
    # Establecer valor por defecto útil en desarrollo local
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/udc_netschool')

class ProductionConfig(Config):
    DEBUG = False
    # En producción, estas variables DEBEN estar definidas como variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

class TestingConfig(Config):
    TESTING = True
    # Usar puerto por defecto de MongoDB para pruebas también
    MONGODB_URI = 'mongodb://localhost:27017/test_myapp'

 # Configuración de archivos  
    UPLOAD_FOLDER = 'uploads'  
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo  
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}