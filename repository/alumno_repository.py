from sqlalchemy.orm import Session
from typing import List, Optional
from domain.alumno_interface import AlumnoRepository
from models.models import Alumno


class AlumnoRepositoryImpl(AlumnoRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_alumnos(self) -> List[Alumno]:
        return self.db.query(Alumno).all()

    def obtener_alumno_por_matricula(self, matricula: str) -> Optional[Alumno]:
        return self.db.query(Alumno).filter(Alumno.matricula == matricula).first()

    def registrar_alumno(self, alumno: Alumno) -> Alumno:
        self.db.add(alumno)
        self.db.commit()
        return alumno

