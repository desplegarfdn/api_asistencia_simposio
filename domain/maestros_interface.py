from abc import ABC, abstractmethod
from typing import List, Optional
from models.models import Maestro


class MaestroRepository(ABC):
    @abstractmethod
    def obtener_maestros(self) -> List[Maestro]:
        pass

    @abstractmethod
    def obtener_maestro_por_plaza(self, numero_plaza: str) -> Optional[Maestro]:
        pass

    @abstractmethod
    def registrar_maestro(self, maestro: Maestro) -> Maestro:
        pass
