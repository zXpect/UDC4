from flask import Flask, render_template, redirect, url_for, session, abort  
from flask_session import Session  
import logging  
from logging.handlers import RotatingFileHandler  
import os 
from config import Config  
from routes.public import public  
from routes.auth import auth  
from routes.admin import admin  
from routes.student import student  
from routes.parent import parent  
from routes.teacher import teacher  
  
def create_app():  
    app = Flask(__name__)  
    app.config.from_object(Config)  
      
    # Configurar logging  
    if not app.debug:  
        if not os.path.exists('logs'):  
            os.mkdir('logs')  
        file_handler = RotatingFileHandler('logs/udc.log', maxBytes=10240, backupCount=10)  
        file_handler.setFormatter(logging.Formatter(  
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'  
        ))  
        file_handler.setLevel(logging.INFO)  
        app.logger.addHandler(file_handler)  
        app.logger.setLevel(logging.INFO)  
        app.logger.info('UDC NetSchool startup')  

        
    # Configurar sesiones  
    Session(app)  
    
    # Registrar blueprints  
    app.register_blueprint(public, url_prefix='/public')  
    app.register_blueprint(auth, url_prefix='/auth')  
    app.register_blueprint(admin, url_prefix='/admin')  
    app.register_blueprint(student, url_prefix='/student')  
    app.register_blueprint(parent, url_prefix='/parent')  
    app.register_blueprint(teacher, url_prefix='/teacher')  
      

    @app.route('/')  
    def home():  
        return redirect(url_for('public.index'))  

    @app.template_filter('safe_date')  
    def safe_date(value, format='%d/%m/%Y'):  
        if not value:  
            return 'N/A'  
        
        if isinstance(value, str):  
            try:  
                from datetime import datetime  
                # Intenta varios formatos comunes  
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:  
                    try:  
                        value = datetime.strptime(value, fmt)  
                        break  
                    except ValueError:  
                        continue  
                else:  
                    return value  # Si no se puede convertir, devuelve el string original  
            except:  
                return value  
        try:  
            return value.strftime(format)  
        except:  
            return str(value)  
    

    @app.template_filter('safe_float')  
    def safe_float(value, default=0):  
        try:  
            return float(value)  
        except (ValueError, TypeError):  
            return default
  

    # Manejadores de errores  
    @app.errorhandler(404)  
    def not_found_error(error):  
        return render_template('errors/404.html'), 404  
      
    @app.errorhandler(500)  
    def internal_error(error):  
        app.logger.error(f'Server Error: {error}')  
        return render_template('errors/500.html'), 500  
      
    @app.errorhandler(403)  
    def forbidden_error(error):  
        return render_template('errors/403.html'), 403  
    

    
    #Rutas de prueba manejo de errores
    @app.route('/f500')
    def forzar_500():
        raise Exception("¡Error forzado para probar el 500!")
    
    @app.route('/f403')
    def forzar_403():
        abort(403)
      
    return app


  
if __name__ == '__main__':  
    app = create_app()
    app.run(debug=False)