import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 🔹 Cargar las variables del archivo .env
load_dotenv()

# 🔹 Obtener la URL de la BD desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
#


# Crear el motor de conexión a la base de datos
engine = create_engine(DATABASE_URL)

# Configurar sesión de SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas con éxito.")