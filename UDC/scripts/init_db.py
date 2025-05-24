from pymongo import MongoClient
import datetime
import bcrypt

# Conexión a la base de datos
print("Conectando a la base de datos MongoDB...")
client = MongoClient("mongodb://localhost:27017/")
db = client.app_academia_test
print("Conexión exitosa a la base de datos 'app_academia_test'.")

# Insertar usuario docente
print("\nInsertando usuario docente...")
docente_id = db.usuarios.insert_one({
    'username': 'doc.ana',
    'password': bcrypt.hashpw('DocAna2024!'.encode('utf-8'), bcrypt.gensalt()),
    'email': 'ana.gomez@academia.edu',
    'first_name': 'Ana',
    'last_name': 'Gómez',
    'role': 'docente',
    'created_at': datetime.datetime.utcnow(),
    'updated_at': datetime.datetime.utcnow(),
    'active': True
}).inserted_id
print(f"Docente insertado con ID: {docente_id}")

# Insertar usuario alumno
print("\nInsertando usuario alumno...")
alumno_id = db.usuarios.insert_one({
    'username': 'alu.luis',
    'password': bcrypt.hashpw('Luis2024!'.encode('utf-8'), bcrypt.gensalt()),
    'email': 'luis.alumno@academia.edu',
    'first_name': 'Luis',
    'last_name': 'Martínez',
    'role': 'alumno',
    'created_at': datetime.datetime.utcnow(),
    'updated_at': datetime.datetime.utcnow(),
    'active': True
}).inserted_id
print(f"Alumno insertado con ID: {alumno_id}")

# Insertar usuario tutor
print("\nInsertando usuario tutor...")
tutor_id = db.usuarios.insert_one({
    'username': 'tutor.jorge',
    'password': bcrypt.hashpw('Jorge2024!'.encode('utf-8'), bcrypt.gensalt()),
    'email': 'jorge.tutor@academia.edu',
    'first_name': 'Jorge',
    'last_name': 'Martínez',
    'role': 'tutor',
    'created_at': datetime.datetime.utcnow(),
    'updated_at': datetime.datetime.utcnow(),
    'active': True
}).inserted_id
print(f"Tutor insertado con ID: {tutor_id}")

# Relación alumno-tutor
print("\nRelacionando alumno con tutor...")
db.relaciones_tutor.insert_one({
    'alumno_id': alumno_id,
    'tutor_id': tutor_id,
    'created_at': datetime.datetime.utcnow()
})
print("Relación alumno-tutor creada.")

# Crear curso
print("\nCreando curso de Ciencias Naturales...")
curso_id = db.cursos.insert_one({
    'nombre': 'Ciencias Naturales',
    'descripcion': 'Curso introductorio a las ciencias naturales',
    'docente_id': docente_id,
    'nivel': 'Grado 7',
    'created_at': datetime.datetime.utcnow(),
    'active': True
}).inserted_id
print(f"Curso creado con ID: {curso_id}")

# Registrar calificación
print("\nInsertando calificación del alumno...")
db.calificaciones.insert_one({
    'alumno_id': alumno_id,
    'curso_id': curso_id,
    'docente_id': docente_id,
    'valor': 4.8,
    'tipo': 'Examen Final',
    'descripcion': 'Evaluación final del trimestre',
    'created_at': datetime.datetime.utcnow()
})
print("Calificación registrada correctamente.")

# Cargar archivo institucional
print("\nCargando archivo institucional...")
db.archivos_institucionales.insert_one({
    'titulo': 'Manual de Convivencia',
    'descripcion': 'Guía de normas y comportamiento institucional',
    'ruta_archivo': '/documentos/manual_convivencia.pdf',
    'tipo_archivo': 'pdf',
    'categoria': 'normas',
    'cargado_por': docente_id,
    'created_at': datetime.datetime.utcnow(),
    'active': True
})
print("Archivo institucional cargado exitosamente.")

# Crear evento institucional
print("\nCreando evento institucional...")
db.eventos.insert_one({
    'titulo': 'Feria de Ciencias',
    'fecha': '2025-09-10',
    'hora': '08:30',
    'lugar': 'Salón Principal',
    'descripcion': 'Presentación de proyectos científicos escolares',
    'created_at': datetime.datetime.utcnow()
})
print("Evento creado correctamente.")

# Enviar notificación
print("\nEnviando notificación al alumno...")
db.notificaciones.insert_one({
    'usuario_id': alumno_id,
    'titulo': 'Invitación a Feria de Ciencias',
    'mensaje': 'Participa en la feria este 10 de septiembre.',
    'tipo': 'evento',
    'datos': {},
    'leido': False,
    'created_at': datetime.datetime.utcnow()
})
print("Notificación enviada correctamente.")

# Finalización
print("\n>>> TODOS LOS DATOS HAN SIDO INSERTADOS CORRECTAMENTE.")
print(f"ID del Docente: {docente_id}")
print(f"ID del Alumno: {alumno_id}")
print(f"ID del Tutor: {tutor_id}")
print(f"ID del Curso: {curso_id}")
