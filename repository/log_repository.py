from typing import List, Tuple, Any, Dict
from sqlalchemy import Row
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from models.models import LogActividad
from domain.log_interface import LogRepository


class LogRepositoryImpl(LogRepository):
    def __init__(self, db: Session):
        self.db = db

    def registrar_log(self, usuario_id: int, username: str, endpoint: str, metodo: str, mensaje: str):
        nuevo_log = LogActividad(
            usuario_id=usuario_id,
            username=username,
            endpoint=endpoint,
            metodo=metodo,
            mensaje=mensaje
        )
        self.db.add(nuevo_log)
        self.db.commit()
        self.db.refresh(nuevo_log)
        return nuevo_log

    def obtener_logs(self):
        return self.db.query(LogActividad).all()

    def contar_registros_por_usuario(self) -> List[Dict[str, Any]]:
        resultados: List[Row] = (
            self.db.query(
                LogActividad.username,
                func.count().filter(LogActividad.endpoint == "/entrada").label("total_entradas"),
                func.count().filter(LogActividad.endpoint == "/salida").label("total_salidas")
            )
            .group_by(LogActividad.username)
            .all()
        )

        # Convertir resultados a una lista de diccionarios
        return [
            {
                "username": row[0],
                "total_entradas": row[1] if row[1] is not None else 0,
                "total_salidas": row[2] if row[2] is not None else 0
            }
            for row in resultados
        ]