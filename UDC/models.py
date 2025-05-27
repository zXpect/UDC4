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
        # Convert date string to datetime object
        try:
            if isinstance(date, str):
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD")
            
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
            # Convert date string to datetime object
            if isinstance(date, str):
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                
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
            print(f"=== Event.delete called with event_id: {event_id} (type: {type(event_id)}) ===")
            
            # Convertir a string si es ObjectId
            if isinstance(event_id, ObjectId):
                event_id_str = str(event_id)
            else:
                event_id_str = event_id
                
            print(f"=== Working with event_id_str: {event_id_str} ===")
            
            # Verificar que el ID sea válido
            if not ObjectId.is_valid(event_id_str):
                print(f"=== Invalid ObjectId format: {event_id_str} ===")
                return False
                
            # Crear ObjectId para la consulta
            object_id = ObjectId(event_id_str)
            print(f"=== Created ObjectId: {object_id} ===")
            
            # Verificar que el evento exista antes de intentar eliminarlo
            event = Event.collection.find_one({'_id': object_id})
            print(f"=== Found event: {event is not None} ===")
            if event:
                print(f"=== Event details: {event.get('title', 'No title')} ===")
            
            if not event:
                print(f"=== Event not found in database ===")
                return False
                
            # Intentar eliminar el evento
            print(f"=== Attempting to delete event with ObjectId: {object_id} ===")
            result = Event.collection.delete_one({'_id': object_id})  
            print(f"=== Delete result - deleted_count: {result.deleted_count} ===")
            
            success = result.deleted_count > 0
            print(f"=== Delete operation success: {success} ===")
            return success
            
        except Exception as e:
            print(f"=== ERROR in Event.delete for event_id {event_id}: {str(e)} ===")  
            import traceback
            print(f"=== Full traceback: {traceback.format_exc()} ===")
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
    def create(title, description, file_path, file_type, uploaded_by, category='general', related_task_id=None):  
        file_doc = {  
            'title': title,  
            'description': description,  
            'file_path': file_path,  
            'file_type': file_type,  
            'category': category,  
            'uploaded_by': uploaded_by,  
            'created_at': datetime.datetime.utcnow(),  
            'active': True,
            'related_task_id': ObjectId(related_task_id) if related_task_id and ObjectId.is_valid(related_task_id) else None
        }  
        result = InstitutionalFile.collection.insert_one(file_doc)  
        return result.inserted_id  
      
    @staticmethod  
    def find_all():  
        return list(InstitutionalFile.collection.find({'active': True}).sort('created_at', -1))  

    @staticmethod
    def find_all_for_role(role, user_id=None):
        """Fetches files appropriate for the given user role."""
        query = {'active': True}
        
        if role == 'public':
            query['category'] = 'general'
        elif role == 'student':
            # Students can see general, academic, and task-related files
            query['category'] = {'$in': ['general', 'academic', 'tasks']}
        elif role == 'teacher':
            # Teachers see all active files, plus their own uploads even if marked differently by an admin later
            # For simplicity now, teachers see all active categories.
            # More specific logic (e.g., only their tasks) could be added if needed.
            query['category'] = {'$in': ['general', 'academic', 'tasks', 'teacher_specific']} # teacher_specific or similar for private teacher files
        elif role == 'parent':
            # Parents see general and academic files.
            # Future: could be refined to files related to their children's courses/grades
            query['category'] = {'$in': ['general', 'academic']}
        elif role == 'admin':
            # Admins see all files, including inactive ones if needed for management (but find_all_for_role usually implies active)
            return list(InstitutionalFile.collection.find().sort('created_at', -1)) # Admin sees all
        else: # Default to public if role is unknown
            query['category'] = 'general'
            
        return list(InstitutionalFile.collection.find(query).sort('created_at', -1))

    @staticmethod
    def can_user_access_file(user_role, user_id, file_doc):
        """Checks if a user with a given role and ID can access/download a specific file document."""
        if not file_doc or not file_doc.get('active'):
            return False

        category = file_doc.get('category')
        uploader_id = file_doc.get('uploaded_by')

        if user_role == 'admin':
            return True
        
        if user_role == 'public':
            return category == 'general'
            
        if user_role == 'student':
            return category in ['general', 'academic', 'tasks']
            
        if user_role == 'teacher':
            # Teachers can access general, academic, tasks, their own uploads, or teacher_specific files.
            return category in ['general', 'academic', 'tasks', 'teacher_specific'] or (uploader_id and user_id and ObjectId(user_id) == uploader_id)

        if user_role == 'parent':
            return category in ['general', 'academic']
            
        return False

    @staticmethod  
    def find_by_category(category):  
        return list(InstitutionalFile.collection.find({'category': category, 'active': True}))  
      

    @staticmethod
    def delete(file_id):
        try:
            print(f"=== InstitutionalFile.delete called with file_id: {file_id} (type: {type(file_id)}) ===")
            
            # Convertir a string si es ObjectId
            if isinstance(file_id, ObjectId):
                file_id_str = str(file_id)
            else:
                file_id_str = file_id
            
            print(f"=== Working with file_id_str: {file_id_str} ===")
            
            # Verificar que el ID sea válido
            if not ObjectId.is_valid(file_id_str):
                print(f"=== Invalid ObjectId format: {file_id_str} ===")
                return False
            
            # Crear ObjectId para la consulta
            object_id = ObjectId(file_id_str)
            print(f"=== Created ObjectId: {object_id} ===")
            
            # Verificar que el archivo exista antes de intentar eliminarlo
            file_doc = InstitutionalFile.collection.find_one({'_id': object_id})
            print(f"=== Found file: {file_doc is not None} ===")
            if file_doc:
                print(f"=== File details: {file_doc.get('title', 'No title')} ===")
            
            if not file_doc:
                print(f"=== File not found in database ===")
                return False
            
            # Intentar eliminar el archivo
            print(f"=== Attempting to delete file with ObjectId: {object_id} ===")
            result = InstitutionalFile.collection.delete_one({'_id': object_id})
            
            print(f"=== Delete result - deleted_count: {result.deleted_count} ===")
            print(f"=== Delete result - acknowledged: {result.acknowledged} ===")
            
            success = result.deleted_count > 0
            print(f"=== Delete operation success: {success} ===")
            return success
            
        except Exception as e:
            print(f"=== ERROR in InstitutionalFile.delete for file_id {file_id}: {str(e)} ===")
            import traceback
            print(f"=== Full traceback: {traceback.format_exc()} ===")
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

    @staticmethod
    def find_by_teacher_id(teacher_id):
        """Find all active courses assigned to a specific teacher."""
        if not ObjectId.is_valid(teacher_id):
            return []
        return list(Course.collection.find({'teacher_id': ObjectId(teacher_id), 'active': True}))

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

class CourseEnrollment:
    collection = db.course_enrollments

    @staticmethod
    def enroll_student(course_id, student_id, enrolled_by_user_id):
        """Enroll a student in a course if not already enrolled."""
        if not ObjectId.is_valid(course_id) or not ObjectId.is_valid(student_id):
            raise ValueError("Invalid course_id or student_id")

        existing_enrollment = CourseEnrollment.collection.find_one({
            'course_id': ObjectId(course_id),
            'student_id': ObjectId(student_id)
        })
        if existing_enrollment:
            # Optionally, you could update the enrollment or just return it
            return existing_enrollment['_id'] # Or raise an error/return None

        enrollment_doc = {
            'course_id': ObjectId(course_id),
            'student_id': ObjectId(student_id),
            'enrolled_at': datetime.datetime.utcnow(),
            'enrolled_by': ObjectId(enrolled_by_user_id) if ObjectId.is_valid(enrolled_by_user_id) else None,
            'active': True # Using active for potential soft unenrollment
        }
        result = CourseEnrollment.collection.insert_one(enrollment_doc)
        return result.inserted_id

    @staticmethod
    def unenroll_student(course_id, student_id):
        """Unenroll a student from a course (soft delete)."""
        if not ObjectId.is_valid(course_id) or not ObjectId.is_valid(student_id):
            raise ValueError("Invalid course_id or student_id")
            
        # result = CourseEnrollment.collection.delete_one(
        #     {'course_id': ObjectId(course_id), 'student_id': ObjectId(student_id)}
        # )
        # For soft delete:
        result = CourseEnrollment.collection.update_one(
            {'course_id': ObjectId(course_id), 'student_id': ObjectId(student_id), 'active': True},
            {'$set': {'active': False, 'unenrolled_at': datetime.datetime.utcnow()}}
        )
        return result.modified_count > 0

    @staticmethod
    def get_students_by_course(course_id):
        """Get all active students enrolled in a specific course."""
        if not ObjectId.is_valid(course_id):
            return []
        enrollments = CourseEnrollment.collection.find({
            'course_id': ObjectId(course_id),
            'active': True
        })
        student_ids = [enrollment['student_id'] for enrollment in enrollments]
        if not student_ids:
            return []
        
        students = list(User.collection.find({
            '_id': {'$in': student_ids},
            'role': 'student', # Ensure they are still students
            'active': True
        }))
        return students
    
    @staticmethod
    def get_enrollment_details_for_course(course_id):
        """Get enrollment documents with student details for a course."""
        if not ObjectId.is_valid(course_id):
            return []
        
        pipeline = [
            {
                '$match': {
                    'course_id': ObjectId(course_id),
                    'active': True
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'student_id',
                    'foreignField': '_id',
                    'as': 'student_info'
                }
            },
            {
                '$unwind': '$student_info' # Convert student_info array to object
            },
            {
                '$match': {
                    'student_info.active': True, # Ensure student is active
                    'student_info.role': 'student'
                }
            },
            {
                '$project': {
                    '_id': 1, # Enrollment ID
                    'course_id': 1,
                    'student_id': 1,
                    'enrolled_at': 1,
                    'student_username': '$student_info.username',
                    'student_first_name': '$student_info.first_name',
                    'student_last_name': '$student_info.last_name',
                    'student_email': '$student_info.email'
                }
            }
        ]
        return list(CourseEnrollment.collection.aggregate(pipeline))

    @staticmethod
    def get_courses_by_student(student_id):
        """Get all active courses a specific student is enrolled in."""
        if not ObjectId.is_valid(student_id):
            return []
        
        pipeline = [
            {
                '$match': {
                    'student_id': ObjectId(student_id),
                    'active': True
                }
            },
            {
                '$lookup': {
                    'from': 'courses',
                    'localField': 'course_id',
                    'foreignField': '_id',
                    'as': 'course_info'
                }
            },
            {
                '$unwind': '$course_info'
            },
            {
                '$match': {
                    'course_info.active': True # Ensure the course itself is active
                }
            },
            {
                '$lookup': { # Second lookup to get teacher's name for the course
                    'from': 'users',
                    'localField': 'course_info.teacher_id',
                    'foreignField': '_id',
                    'as': 'teacher_info'
                }
            },
            {
                '$unwind': {
                    'path': '$teacher_info',
                    'preserveNullAndEmptyArrays': True # Keep course if teacher not found/assigned
                }
            },
            {
                '$project': {
                    '_id': '$course_info._id',
                    'name': '$course_info.name',
                    'description': '$course_info.description',
                    'grade_level': '$course_info.grade_level',
                    'teacher_id': '$course_info.teacher_id',
                    'teacher_name': {
                        '$concat': [
                            {'$ifNull': ['$teacher_info.first_name', '']},
                            ' ',
                            {'$ifNull': ['$teacher_info.last_name', '']}
                        ]
                    },
                    'enrolled_at': '$enrolled_at'
                }
            },
            {
                '$addFields': { # Trim the teacher_name if it ends up being just a space
                    'teacher_name': {
                        '$trim': {'input': '$teacher_name'}
                    }
                }
            }
        ]
        
        courses = list(CourseEnrollment.collection.aggregate(pipeline))
        # Replace empty or space-only teacher names with 'N/A'
        for course in courses:
            if not course['teacher_name'] or course['teacher_name'].isspace():
                course['teacher_name'] = 'N/A'
        return courses

    @staticmethod
    def get_available_students_for_course(course_id):
        """Get students who are not actively enrolled in the specified course."""
        if not ObjectId.is_valid(course_id):
            return list(User.collection.find({'role': 'student', 'active': True}))

        enrolled_student_ids = [
            enrollment['student_id'] for enrollment in 
            CourseEnrollment.collection.find({'course_id': ObjectId(course_id), 'active': True}, {'student_id': 1})
        ]
        
        available_students = list(User.collection.find({
            'role': 'student',
            'active': True,
            '_id': {'$nin': enrolled_student_ids}
        }))
        return available_students

class Task:
    collection = db.tasks

    @staticmethod
    def create(course_id, teacher_id, title, description, due_date, file_path=None):
        """Create a new task."""
        if not ObjectId.is_valid(course_id) or not ObjectId.is_valid(teacher_id):
            raise ValueError("Invalid course_id or teacher_id")
        
        try:
            # Ensure due_date is a datetime object if it's a string
            if isinstance(due_date, str):
                due_datetime = datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M') # Expecting YYYY-MM-DDTHH:MM
            elif isinstance(due_date, datetime.datetime):
                due_datetime = due_date
            else:
                raise ValueError("Invalid due_date format. Expected datetime object or string YYYY-MM-DDTHH:MM")
        except ValueError as e:
            raise ValueError(f"Error parsing due_date: {e}. Expected format YYYY-MM-DDTHH:MM")


        task_doc = {
            'course_id': ObjectId(course_id),
            'teacher_id': ObjectId(teacher_id),
            'title': title,
            'description': description,
            'due_date': due_datetime,
            'file_path': file_path, # Relative path to the uploaded file
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow(),
            'active': True
        }
        result = Task.collection.insert_one(task_doc)
        return result.inserted_id

    @staticmethod
    def find_by_id(task_id):
        """Find a task by its ID."""
        if not ObjectId.is_valid(task_id):
            return None
        return Task.collection.find_one({'_id': ObjectId(task_id), 'active': True})

    @staticmethod
    def find_by_course_id(course_id):
        """Find all active tasks for a specific course, ordered by due_date."""
        if not ObjectId.is_valid(course_id):
            return []
        return list(Task.collection.find({
            'course_id': ObjectId(course_id),
            'active': True
        }).sort('due_date', 1))

    @staticmethod
    def find_by_teacher_id(teacher_id):
        """Find all active tasks created by a specific teacher, ordered by due_date."""
        if not ObjectId.is_valid(teacher_id):
            return []
        # To also get course name, we might need an aggregation here or handle it in the route
        return list(Task.collection.find({
            'teacher_id': ObjectId(teacher_id),
            'active': True
        }).sort('due_date', 1))
    
    @staticmethod
    def find_by_teacher_id_with_course_info(teacher_id):
        """Find all active tasks by a teacher, including course name."""
        if not ObjectId.is_valid(teacher_id):
            return []
        pipeline = [
            {
                '$match': {
                    'teacher_id': ObjectId(teacher_id),
                    'active': True
                }
            },
            {
                '$lookup': {
                    'from': 'courses',
                    'localField': 'course_id',
                    'foreignField': '_id',
                    'as': 'course_info'
                }
            },
            {
                '$unwind': {
                    'path': '$course_info',
                    'preserveNullAndEmptyArrays': True # Keep task if course is somehow missing
                }
            },
            {
                '$addFields': {
                    'course_name': '$course_info.name'
                }
            },
            {
                '$sort': {'due_date': 1}
            }
        ]
        return list(Task.collection.aggregate(pipeline))

    @staticmethod
    def update(task_id, update_data):
        """Update a task."""
        if not ObjectId.is_valid(task_id):
            return False
        
        if 'due_date' in update_data and isinstance(update_data['due_date'], str):
            try:
                update_data['due_date'] = datetime.datetime.strptime(update_data['due_date'], '%Y-%m-%dT%H:%M')
            except ValueError as e:
                # Or handle this error more gracefully depending on requirements
                raise ValueError(f"Error parsing due_date for update: {e}")

        update_data['updated_at'] = datetime.datetime.utcnow()
        result = Task.collection.update_one(
            {'_id': ObjectId(task_id), 'active': True},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(task_id):
        """Soft delete a task."""
        if not ObjectId.is_valid(task_id):
            return False
        result = Task.collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {'active': False, 'updated_at': datetime.datetime.utcnow()}}
        )
        return result.modified_count > 0

    # Placeholder for student submissions if needed later
    # @staticmethod
    # def add_submission(task_id, student_id, file_path, submission_date):
    #     pass
    # @staticmethod
    # def get_submissions(task_id):
    #     pass