# Configuración de la base de datos
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from database.database import Base


class Alumno(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String, unique=True, index=True)
    nombre = Column(String)
    apellido_p = Column(String)
    apellido_m = Column(String)
    carrera = Column(String)
    semestre = Column(Integer)
    grupo = Column(String)
    genero = Column(String)

class Maestro(Base):
    __tablename__ = "maestros"
    id = Column(Integer, primary_key=True, index=True)
    numero_plaza = Column(String, unique=True, index=True)
    nombre = Column(String)
    apellido_p = Column(String)
    apellido_m = Column(String)
    genero = Column(String)

class Asistencia(Base):
    __tablename__ = "asistencias"
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(String, index=True)
    tipo_persona = Column(String)  # Puede ser 'alumno' o 'maestro'
    fecha_entrada = Column(DateTime, default=datetime.utcnow)
    fecha_salida = Column(DateTime, nullable=True)

    alumno_id = Column(String, ForeignKey("alumnos.matricula"), nullable=True)
    maestro_id = Column(String, ForeignKey("maestros.numero_plaza"), nullable=True)

    alumno = relationship("Alumno", foreign_keys=[alumno_id])
    maestro = relationship("Maestro", foreign_keys=[maestro_id])

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    nombre = Column(String)
    apellido_paterno = Column(String)
    apellido_materno = Column(String)
    role= Column(String)