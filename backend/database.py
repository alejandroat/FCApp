import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class DBConnection:
    """Adaptador para que psycopg2 se comporte como sqlite3"""
    def __init__(self):
        # Conectamos a la base de datos
        self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
    def execute(self, query, params=None):
        # Creamos un cursor, ejecutamos y lo devolvemos para poder usar .fetchone() o .fetchall()
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_connection():
    return DBConnection()

def init_db():
    """Crea las tablas si no existen"""
    try:
        conn = get_connection()
        
        # Tabla de usuarios
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL
            )
        """)
        
        # Tabla de jugadores
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jugadores (
                id SERIAL PRIMARY KEY,
                dorsal INTEGER,
                nombre TEXT NOT NULL,
                valoracion INTEGER NOT NULL,
                posicion_principal TEXT NOT NULL,
                posicion_secundaria TEXT,
                pais TEXT NOT NULL,
                equipo TEXT,
                equipacion TEXT,
                rango INTEGER CHECK (rango >= 0 AND rango <= 5),
                habilitado INTEGER DEFAULT 1,
                programa TEXT,
                imagen_url TEXT,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de caché de imágenes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS imagenes_cache (
                id SERIAL PRIMARY KEY,
                nombre_busqueda TEXT NOT NULL UNIQUE,
                imagen_url TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dias_validez INTEGER DEFAULT 30
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente en la nube (Neon).")
    except Exception as e:
        print(f"❌ Error inicializando la base de datos: {e}")
        raise