from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_db
from models.schemas import UsuarioSchema
from repository.usuario_repository import UsuarioRepositoryImpl
from auth.auth import create_access_token, verify_password, get_current_user
from datetime import timedelta

router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario_repo = UsuarioRepositoryImpl(db)
    usuario = usuario_repo.obtener_usuario_por_username(form_data.username)

    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    # Crear token JWT
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": usuario.username, "role": usuario.role}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user/me", response_model=UsuarioSchema)
def leer_usuarios_me(current_user: UsuarioSchema = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user