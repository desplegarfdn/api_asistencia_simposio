from typing import Optional
from domain.usuario_interface import UsuarioRepository
from models.models import Usuario


class UsuarioService:
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def obtener_usuario_por_username(self, username: str) -> Optional[Usuario]:
        return self.repository.obtener_usuario_por_username(username)

    def registrar_usuario(self, usuario: Usuario) -> Usuario:
        return self.repository.registrar_usuario(usuario)

    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        return self.repository.actualizar_usuario(usuario)

    def eliminar_usuario(self, username: str) -> None:
        self.repository.eliminar_usuario(username)
