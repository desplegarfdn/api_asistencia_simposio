from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from auth.auth import get_current_user
from database.database import get_db
from models.models import Maestro
from models.schemas import MaestroSchema
from repository.maestros_repository import MaestroRepositoryImpl
from service.maestros_service import MaestroService

router = APIRouter()


@router.get("/todos", response_model=List[MaestroSchema])
def obtener_maestros(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver maestros")

    service = MaestroService(MaestroRepositoryImpl(db))
    return service.obtener_maestros()


@router.get("/buscar/{numero_plaza}", response_model=MaestroSchema)
def obtener_maestro(numero_plaza: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este maestro")

    service = MaestroService(MaestroRepositoryImpl(db))
    maestro = service.obtener_maestro_por_plaza(numero_plaza)
    if not maestro:
        raise HTTPException(status_code=404, detail="Maestro no encontrado")
    return maestro


@router.post("/crear", response_model=MaestroSchema)
def registrar_maestro(maestro: MaestroSchema, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar maestros")

    service = MaestroService(MaestroRepositoryImpl(db))
    return service.registrar_maestro(Maestro(**maestro.dict()))
