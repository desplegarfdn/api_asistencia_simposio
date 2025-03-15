from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from domain.asistencia_interface import AsistenciaRepository
from models.models import Asistencia, Alumno, Maestro


class AsistenciaRepositoryImpl(AsistenciaRepository):
    def __init__(self, db: Session):
        self.db = db

    def registrar_entrada(self, persona_id: str, tipo_persona: str, fecha_entrada: datetime) -> Asistencia:
        asistencia = Asistencia(persona_id=persona_id, tipo_persona=tipo_persona, fecha_entrada=fecha_entrada)
        self.db.add(asistencia)
        self.db.commit()
        self.db.refresh(asistencia)
        return asistencia

    def registrar_salida(self, persona_id: str, fecha_salida: datetime) -> Optional[Asistencia]:
        """Registra la hora de salida para una persona que ya tiene asistencia registrada."""

        asistencia = self.db.query(Asistencia).filter(
            Asistencia.persona_id == persona_id,
            Asistencia.fecha_salida == None
        ).first()

        if not asistencia:
            return None  # No hay asistencia activa

        # 🔹 Actualizar la fecha de salida con GMT-6
        asistencia.fecha_salida = fecha_salida

        self.db.commit()
        self.db.refresh(asistencia)
        return asistencia

    def buscar_asistencia(self, persona_id: str) -> Optional[Asistencia]:
        return self.db.query(Asistencia).filter(Asistencia.persona_id == persona_id).first()
