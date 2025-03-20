from typing import List, Dict, Any
from repository.log_repository import LogRepository

class LogService:
    def __init__(self, log_repo: LogRepository):
        self.log_repo = log_repo

    def registrar_log(self, usuario_id: int, username: str, endpoint: str, metodo: str, mensaje: str):
        return self.log_repo.registrar_log(usuario_id, username, endpoint, metodo, mensaje)

    def obtener_logs(self):
        return self.log_repo.obtener_logs()

    def contar_registros_por_usuario(self) -> List[Dict[str, Any]]:
        return self.log_repo.contar_registros_por_usuario()