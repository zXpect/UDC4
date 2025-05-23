from flask import Blueprint, render_template, session, redirect, url_for, flash  
from routes.auth import login_required, role_required  
from models import Event, Grade, Course  
  
student = Blueprint('student', __name__)  
  
@student.route('/')  
@login_required  
@role_required('student')  
def dashboard():  
    events = Event.find_all()[:5]  # Últimos 5 eventos  
    student_id = session.get('user_id')  
    grades = Grade.find_by_student(student_id)  
      
    return render_template('student/dashboard.html', events=events, grades=grades)  
  
@student.route('/events')  
@login_required  
@role_required('student')  
def events():  
    events = Event.find_all()  
    return render_template('student/events.html', events=events)  
  
@student.route('/grades')  
@login_required  
@role_required('student')  
def grades():  
    student_id = session.get('user_id')  
    grades = Grade.find_by_student(student_id)  
    return render_template('student/grades.html', grades=grades)