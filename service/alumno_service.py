from typing import List, Optional
from domain.alumno_interface import AlumnoRepository
from models.models import Alumno


class AlumnoService:
    def __init__(self, repository: AlumnoRepository):
        self.repository = repository

    def obtener_alumnos(self) -> List[Alumno]:
        return self.repository.obtener_alumnos()

    def obtener_alumno_por_matricula(self, matricula: str) -> Optional[Alumno]:
        return self.repository.obtener_alumno_por_matricula(matricula)

    def registrar_alumno(self, alumno: Alumno) -> Alumno:
        return self.repository.registrar_alumno(alumno)
