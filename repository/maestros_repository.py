from sqlalchemy.orm import Session
from typing import List, Optional
from domain.maestros_interface import MaestroRepository
from models.models import Maestro


class MaestroRepositoryImpl(MaestroRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_maestros(self) -> List[Maestro]:
        return self.db.query(Maestro).all()

    def obtener_maestro_por_plaza(self, numero_plaza: str) -> Optional[Maestro]:
        return self.db.query(Maestro).filter(Maestro.numero_plaza == numero_plaza).first()

    def registrar_maestro(self, maestro: Maestro) -> Maestro:
        self.db.add(maestro)
        self.db.commit()
        return maestro