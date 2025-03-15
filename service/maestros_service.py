from typing import List, Optional
from domain.maestros_interface import MaestroRepository
from models.models import Maestro


class MaestroService:
    def __init__(self, repository: MaestroRepository):
        self.repository = repository

    def obtener_maestros(self) -> List[Maestro]:
        return self.repository.obtener_maestros()

    def obtener_maestro_por_plaza(self, numero_plaza: str) -> Optional[Maestro]:
        return self.repository.obtener_maestro_por_plaza(numero_plaza)

    def registrar_maestro(self, maestro: Maestro) -> Maestro:
        return self.repository.registrar_maestro(maestro)