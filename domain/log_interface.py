from abc import ABC, abstractmethod
from typing import List, Tuple

from models.models import LogActividad

class LogRepository(ABC):
    @abstractmethod
    def registrar_log(self, usuario_id: int, username: str, endpoint: str, metodo: str, mensaje: str):
        pass

    @abstractmethod
    def obtener_logs(self):
        pass

    @abstractmethod
    def contar_registros_por_usuario(self) -> List[Tuple[str, int, int]]:
        """Devuelve un conteo de entradas y salidas registradas por cada usuario."""
        pass