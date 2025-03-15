from abc import ABC, abstractmethod
from typing import List, Optional
from models.models import Alumno


class AlumnoRepository(ABC):
    @abstractmethod
    def obtener_alumnos(self) -> List[Alumno]:
        pass

    @abstractmethod
    def obtener_alumno_por_matricula(self, matricula: str) -> Optional[Alumno]:
        pass

    @abstractmethod
    def registrar_alumno(self, alumno: Alumno) -> Alumno:
        pass