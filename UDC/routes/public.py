from flask import Blueprint, render_template  
from models import Event  
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