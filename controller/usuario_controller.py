from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.auth import get_current_user, hash_password
from database.database import get_db
from models.models import Usuario
from models.schemas import UsuarioSchema, UsuarioCreateSchema
from repository.usuario_repository import UsuarioRepositoryImpl
from service.usuario_service import UsuarioService

router = APIRouter()


@router.get("/buscar/{username}", response_model=UsuarioSchema)
def obtener_usuario(username: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para ver usuarios")

    service = UsuarioService(UsuarioRepositoryImpl(db))
    usuario = service.obtener_usuario_por_username(username)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/crear", response_model=UsuarioSchema)
def registrar_usuario(usuario: UsuarioCreateSchema, db: Session = Depends(get_db)):
    service = UsuarioService(UsuarioRepositoryImpl(db))

    # 🔹 Encriptar la contraseña antes de guardarla
    hashed_password = hash_password(usuario.password)

    nuevo_usuario = Usuario(
        username=usuario.username,
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        hashed_password=hashed_password,  # Ahora sí se almacena correctamente
        role=usuario.role
    )

    return service.registrar_usuario(nuevo_usuario)


@router.put("/editar/{username}", response_model=UsuarioSchema)
def actualizar_usuario(username: str, usuario: UsuarioSchema, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar usuarios")

    service = UsuarioService(UsuarioRepositoryImpl(db))
    return service.actualizar_usuario(Usuario(**usuario.dict()))


@router.delete("/eliminar/{username}")
def eliminar_usuario(username: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios")

    service = UsuarioService(UsuarioRepositoryImpl(db))
    service.eliminar_usuario(username)
    return {"mensaje": "Usuario eliminado"}
