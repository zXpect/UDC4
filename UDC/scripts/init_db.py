import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient  
from config import Config  
import bcrypt  
import datetime  
import sys


  
def init_database():  
    """Inicializa la base de datos con colecciones y datos iniciales"""  
      
    try:  
        # Conectar a MongoDB  
        client = MongoClient(Config.MONGODB_URI)  
        db = client.udc_netschool  
          
        print("Conectado a MongoDB Atlas exitosamente")  
          
        # Crear índices para optimizar consultas  
        print("Creando índices...")  
          
        # Índices para usuarios  
        db.users.create_index("username", unique=True)  
        db.users.create_index("role")  
          
        # Índices para eventos  
        db.events.create_index("date")  
        db.events.create_index("title")  
          
        print("Índices creados exitosamente")  
          
        # Crear usuarios iniciales  
        print("Creando usuarios iniciales...")  
          
        users = [  
            {'username': 'admin', 'password': 'admin123', 'role': 'admin'},  
            {'username': 'teacher', 'password': 'teacher123', 'role': 'teacher'},  
            {'username': 'student', 'password': 'student123', 'role': 'student'}  
        ]  
          
        for user_data in users:  
            # Verificar si el usuario ya existe  
            existing_user = db.users.find_one({'username': user_data['username']})  
            if not existing_user:  
                hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())  
                user = {  
                    'username': user_data['username'],  
                    'password': hashed_password,  
                    'role': user_data['role'],  
                    'created_at': datetime.datetime.utcnow(),  
                    'active': True  
                }  
                db.users.insert_one(user)  
                print(f"Usuario {user_data['username']} creado")  
            else:  
                print(f"Usuario {user_data['username']} ya existe")  
          
        # Crear eventos iniciales  
        print("Creando eventos iniciales...")  
          
        events = [  
            {  
                'title': 'Reunión de Padres',  
                'date': '2025-05-15',  
                'time': '18:00',  
                'location': 'Auditorio Principal',  
                'description': 'Reunión informativa para padres de familia.',  
                'created_at': datetime.datetime.utcnow()  
            },  
            {  
                'title': 'Día del Maestro',  
                'date': '2025-05-20',  
                'time': '10:00',  
                'location': 'Patio Central',  
                'description': 'Celebración por el día del maestro.',  
                'created_at': datetime.datetime.utcnow()  
            },  
            {  
                'title': 'Exámenes Finales',  
                'date': '2025-06-01',  
                'time': '08:00',  
                'location': 'Aulas 101-105',  
                'description': 'Período de exámenes finales del semestre.',  
                'created_at': datetime.datetime.utcnow()  
            }  
        ]  
        
          
        # Verificar si ya existen eventos  
        existing_events = db.events.count_documents({})  
        if existing_events == 0:  
            db.events.insert_many(events)  
            print(f"{len(events)} eventos creados")  
        else:  
            print(f"Ya existen {existing_events} eventos en la base de datos")  
          
        # Mostrar estadísticas  
        print("\n=== ESTADÍSTICAS DE LA BASE DE DATOS ===")  
        print(f"Usuarios totales: {db.users.count_documents({})}")  
        print(f"Eventos totales: {db.events.count_documents({})}")  
          
        # Mostrar usuarios por rol  
        for role in ['admin', 'teacher', 'student']:  
            count = db.users.count_documents({'role': role})  
            print(f"Usuarios {role}: {count}")  
          
        print("\nBase de datos inicializada correctamente")  
          
    except Exception as e:  
        print(f"Error al inicializar la base de datos: {e}")  
        return False  
      
    return True  
  
def reset_database():  
    """Elimina todas las colecciones y reinicia la base de datos"""  
    try:  
        client = MongoClient(Config.MONGODB_URI)  
        db = client.udc_netschool  
          
        # Eliminar todas las colecciones  
        db.users.drop()  
        db.events.drop()  
          
        print("Base de datos reiniciada")  
          
        # Reinicializar  
        return init_database()  
          
    except Exception as e:  
        print(f"Error al reiniciar la base de datos: {e}")  
        return False  
  
if __name__ == '__main__':  
    import sys  
      
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':  
        reset_database()  
    else:  
        init_database()

