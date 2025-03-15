from abc import ABC, abstractmethod
from typing import Optional
from models.models import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def obtener_usuario_por_username(self, username: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def registrar_usuario(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def eliminar_usuario(self, username: str) -> None:
        pass
