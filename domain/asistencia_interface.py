from abc import abstractmethod, ABC
from datetime import datetime
from typing import Optional
from models.models import Asistencia

class AsistenciaRepository(ABC):
    @abstractmethod
    def registrar_entrada(self, persona_id: str, tipo_persona: str, fecha_entrada: datetime) -> Asistencia:
        pass

    @abstractmethod
    def registrar_salida(self, persona_id: str) -> Optional[Asistencia]:
        pass

    @abstractmethod
    def buscar_asistencia(self, persona_id: str) -> Optional[Asistencia]:
        pass
