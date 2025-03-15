from sqlalchemy.orm import Session
from typing import Optional
from domain.usuario_interface import UsuarioRepository
from models.models import Usuario


class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_usuario_por_username(self, username: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def registrar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        return usuario

    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.merge(usuario)
        self.db.commit()
        return usuario

    def eliminar_usuario(self, username: str) -> None:
        usuario = self.db.query(Usuario).filter(Usuario.username == username).first()
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
