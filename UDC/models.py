from pymongo import MongoClient  
from config import Config  
import datetime  
from bson import ObjectId  
import bcrypt  
import re
from typing import Optional, Dict, Any

client = MongoClient(Config.MONGODB_URI)  
db = client.udc_netschool  

class Event:  
    collection = db.events  
      
    @staticmethod  
    def create(title, date, time, location, description):  
        event = {  
            'title': title,  
            'date': date,  
            'time': time,  
            'location': location,  
            'description': description,  
            'created_at': datetime.datetime.utcnow()  
        }  
        result = Event.collection.insert_one(event)  
        return result.inserted_id  
      
    @staticmethod  
    def find_all():  
        return list(Event.collection.find().sort('date', 1))  
      
    @staticmethod  
    def find_by_id(event_id):  
        try:  
            return Event.collection.find_one({'_id': ObjectId(event_id)})  
        except:  
            return None  
      
    @staticmethod  
    def update(event_id, title, date, time, location, description):  
        try:  
            result = Event.collection.update_one(  
                {'_id': ObjectId(event_id)},  
                {'$set': {  
                    'title': title,  
                    'date': date,  
                    'time': time,  
                    'location': location,  
                    'description': description,  
                    'updated_at': datetime.datetime.utcnow()  
                }}  
            )  
            return result.modified_count > 0  
        except:  
            return False  
      
    @staticmethod  
    def delete(event_id):  
        try:  
            result = Event.collection.delete_one({'_id': ObjectId(event_id)})  
            return result.deleted_count > 0  
        except:  
            return False

class User:  
    collection = db.users  
      
    @staticmethod  
    def find_by_username(username):  
        return User.collection.find_one({'username': username})  
    
    @staticmethod
    def find_by_email(email):
        return User.collection.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        try:
            return User.collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validar formato de username"""
        # Solo letras, números y guiones bajos, entre 4 y 20 caracteres
        pattern = r'^[a-zA-Z0-9_]{4,20}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_password(password):
        """Validar que la contraseña cumpla los requisitos"""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        return True, "Contraseña válida"
    
    @staticmethod
    def validate_name(name):
        """Validar formato de nombre/apellido"""
        if len(name) < 2:
            return False, "Debe tener al menos 2 caracteres"
        
        # Solo letras, espacios y caracteres especiales del español
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(pattern, name):
            return False, "Solo se permiten letras y espacios"
        
        return True, "Nombre válido"
      
    @staticmethod  
    def create_user(username, password, email=None, first_name=None, last_name=None, role='student', **kwargs):  
        """
        Crear un nuevo usuario con validaciones básicas
        """
        
        # Validaciones básicas
        if User.find_by_username(username):  
            raise ValueError("El nombre de usuario ya existe")
        
        if email and User.find_by_email(email):
            raise ValueError("El correo electrónico ya está registrado")
        
        # Hash de la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  
        
        # Crear documento de usuario
        user = {  
            # Campos obligatorios
            'username': username.lower().strip(),
            'password': hashed_password,
            'role': role,
            
            # Campos opcionales
            'email': email.lower().strip() if email else '',
            'first_name': first_name.strip() if first_name else '',
            'last_name': last_name.strip() if last_name else '',
            
            # Metadatos del sistema
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
            'active': True,
        }  
        
        result = User.collection.insert_one(user)  
        return result.inserted_id  
    
    @staticmethod
    def update_user(user_id, update_data):
        """
        Actualizar información del usuario
        """
        try:
            # Agregar timestamp de actualización
            update_data['updated_at'] = datetime.datetime.utcnow()
            
            result = User.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
      
    @staticmethod  
    def verify_password(username, password):  
        """
        Verificar credenciales de usuario
        
        Args:
            username (str): Nombre de usuario o email
            password (str): Contraseña
            
        Returns:
            dict|None: Datos del usuario si las credenciales son válidas
        """
        # Buscar por username o email
        user = User.find_by_username(username)
        if not user:
            user = User.find_by_email(username)
        
        if user and user.get('active', True) and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return user  
        return None  
      
    @staticmethod  
    def get_all_users():  
        """Obtener todos los usuarios activos"""
        return list(User.collection.find({'active': True}))  
      
    @staticmethod  
    def count_users():  
        """Contar usuarios activos"""
        return User.collection.count_documents({'active': True})
    @staticmethod  
    def count_users():  
        return User.collection.count_documents({'active': True})

# Clase para manejar notificaciones de usuarios
class UserNotification:
    collection = db.user_notifications
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info', data=None):
        """
        Crear una nueva notificación para un usuario
        """
        notification = {
            'user_id': ObjectId(user_id),
            'title': title,
            'message': message,
            'type': notification_type,
            'data': data or {},
            'read': False,
            'created_at': datetime.datetime.utcnow(),
        }
        
        result = UserNotification.collection.insert_one(notification)
        return result.inserted_id
    
class InstitutionalFile:  
    collection = db.institutional_files  
      
    @staticmethod  
    def create(title, description, file_path, file_type, uploaded_by, category='general'):  
        file_doc = {  
            'title': title,  
            'description': description,  
            'file_path': file_path,  
            'file_type': file_type,  
            'category': category,  
            'uploaded_by': uploaded_by,  
            'created_at': datetime.datetime.utcnow(),  
            'active': True  
        }  
        result = InstitutionalFile.collection.insert_one(file_doc)  
        return result.inserted_id  
      
    @staticmethod  
    def find_all():  
        return list(InstitutionalFile.collection.find({'active': True}).sort('created_at', -1))  
      
    @staticmethod  
    def find_by_category(category):  
        return list(InstitutionalFile.collection.find({'category': category, 'active': True}))  
      
    @staticmethod  
    def delete(file_id):  
        try:  
            result = InstitutionalFile.collection.update_one(  
                {'_id': ObjectId(file_id)},  
                {'$set': {'active': False}}  
            )  
            return result.modified_count > 0  
        except:  
            return False  
  
class Grade:  
    collection = db.grades  
      
    @staticmethod  
    def create(student_id, course_id, teacher_id, grade_value, grade_type, description=''):  
        grade = {  
            'student_id': ObjectId(student_id),  
            'course_id': ObjectId(course_id),  
            'teacher_id': ObjectId(teacher_id),  
            'grade_value': grade_value,  
            'grade_type': grade_type,  
            'description': description,  
            'created_at': datetime.datetime.utcnow()  
        }  
        result = Grade.collection.insert_one(grade)  
        return result.inserted_id  
      
    @staticmethod  
    def find_by_student(student_id):  
        return list(Grade.collection.find({'student_id': ObjectId(student_id)}))  
      
    @staticmethod  
    def find_by_teacher(teacher_id):  
        return list(Grade.collection.find({'teacher_id': ObjectId(teacher_id)}))  
  
class Course:  
    collection = db.courses  
      
    @staticmethod  
    def create(name, description, teacher_id, grade_level):  
        course = {  
            'name': name,  
            'description': description,  
            'teacher_id': ObjectId(teacher_id),  
            'grade_level': grade_level,  
            'created_at': datetime.datetime.utcnow(),  
            'active': True  
        }  
        result = Course.collection.insert_one(course)  
        return result.inserted_id  
      
    @staticmethod  
    def find_all():  
        return list(Course.collection.find({'active': True}))  
  
class StudentParentRelation:  
    collection = db.student_parent_relations  
      
    @staticmethod  
    def create(student_id, parent_id):  
        """Crear una nueva relación padre-hijo"""
        relation = {  
            'student_id': ObjectId(student_id),  
            'parent_id': ObjectId(parent_id),  
            'created_at': datetime.datetime.utcnow()  
        }  
        result = StudentParentRelation.collection.insert_one(relation)  
        return result.inserted_id  
      
    @staticmethod  
    def find_children_by_parent(parent_id):  
        """Encontrar todos los hijos de un padre específico"""
        relations = list(StudentParentRelation.collection.find({'parent_id': ObjectId(parent_id)}))  
        children = []  
        for relation in relations:  
            child = User.collection.find_one({'_id': relation['student_id']})  
            if child:  
                children.append(child)  
        return children
    
    @staticmethod  
    def verify_parent_child_relationship(parent_id, child_id):  
        """Verificar si existe una relación padre-hijo específica"""
        return StudentParentRelation.collection.find_one({  
            'parent_id': ObjectId(parent_id),  
            'student_id': ObjectId(child_id)  
        }) is not None
  
class InstitutionalInfo:  
    collection = db.institutional_info  
      
    @staticmethod  
    def update_info(key, value, updated_by):  
        try:  
            result = InstitutionalInfo.collection.update_one(  
                {'key': key},  
                {'$set': {  
                    'value': value,  
                    'updated_by': updated_by,  
                    'updated_at': datetime.datetime.utcnow()  
                }},  
                upsert=True  
            )  
            return True  
        except:  
            return False  
      
    @staticmethod  
    def get_info(key):  
        return InstitutionalInfo.collection.find_one({'key': key})  
      
    @staticmethod  
    def get_all_info():  
        return list(InstitutionalInfo.collection.find())