import os  
import sys  
  
# Agregar el directorio actual al path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  
  
from init_db import init_database, reset_database  
  
if __name__ == '__main__':  
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':  
        print("Reiniciando base de datos...")  
        reset_database()  
    else:  
        print("Inicializando base de datos...")  
        init_database()