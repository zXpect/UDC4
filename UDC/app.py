from flask import Flask, render_template, redirect, url_for, session  
from flask_session import Session  
from config import Config  
from routes.public import public  
from routes.auth import auth  
from routes.admin import admin  
from routes.student import student  
from routes.parent import parent  
from routes.teacher import teacher  
  
app = Flask(__name__)  
app.config.from_object(Config)  
  
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
  
  
@app.errorhandler(404)  
def page_not_found(e):  
    return render_template('errors/404.html'), 404  
  
@app.errorhandler(500)  
def internal_server_error(e):  
    return render_template('errors/500.html'), 500  
  
if __name__ == '__main__':  
    app.run(debug=True)