from datetime import datetime, timedelta
from typing import Optional
from domain.asistencia_interface import AsistenciaRepository
from models.models import Asistencia


class AsistenciaService:
    def __init__(self, repository: AsistenciaRepository):
        self.repository = repository

    def registrar_entrada(self, persona_id: str, tipo_persona: str,
                          fecha_entrada: Optional[datetime] = None) -> Asistencia:
        """Registra la entrada de una persona (alumno o maestro) en la asistencia."""

        if fecha_entrada is None:
            fecha_entrada = datetime.utcnow()  # Usar hora actual si no se proporciona

        nueva_asistencia = self.repository.registrar_entrada(persona_id, tipo_persona, fecha_entrada)
        return nueva_asistencia

    def registrar_salida(self, persona_id: str) -> Optional[Asistencia]:
        """Registra la salida de una persona en la asistencia."""

        # 🔹 Obtener la hora actual en GMT-6
        hora_salida = datetime.utcnow() - timedelta(hours=6)

        # 🔹 Llamar al repositorio con la hora corregida
        asistencia_actualizada = self.repository.registrar_salida(persona_id, hora_salida)

        return asistencia_actualizada

    def buscar_asistencia(self, persona_id: str) -> Optional[Asistencia]:
        return self.repository.buscar_asistencia(persona_id)
