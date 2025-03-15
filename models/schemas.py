from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AsistenciaSchema(BaseModel):
    persona_id: str
    tipo_persona: str
    fecha_entrada: datetime
    fecha_salida: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlumnoSchema(BaseModel):
    matricula: str
    nombre: str
    apellido_p: str
    apellido_m: str
    carrera: str
    semestre: int
    grupo: str
    genero: str

    class Config:
        from_attributes = True

class MaestroSchema(BaseModel):
    numero_plaza: str
    nombre: str
    apellido_p: str
    apellido_m: str
    genero: str

    class Config:
        from_attributes = True


class UsuarioCreateSchema(BaseModel):
    username: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    password: str  # Se añade este campo para recibir la contraseña en texto plano
    role: str

    class Config:
        from_attributes = True

class UsuarioSchema(BaseModel):
    username: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    role: str

    class Config:
        from_attributes = True