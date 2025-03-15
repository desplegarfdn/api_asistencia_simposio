from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth.auth import get_current_user
from database.database import get_db
from models.models import Alumno
from models.schemas import AlumnoSchema
from repository.alumno_repository import AlumnoRepositoryImpl
from service.alumno_service import AlumnoService

router = APIRouter()


@router.get("/todos", response_model=List[AlumnoSchema])
def obtener_alumnos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver alumnos")

    service = AlumnoService(AlumnoRepositoryImpl(db))
    return service.obtener_alumnos()


@router.get("/busqueda/{matricula}", response_model=AlumnoSchema)
def obtener_alumno(matricula: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este alumno")

    service = AlumnoService(AlumnoRepositoryImpl(db))
    alumno = service.obtener_alumno_por_matricula(matricula)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno


@router.post("/crear", response_model=AlumnoSchema)
def registrar_alumno(alumno: AlumnoSchema, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar alumnos")

    service = AlumnoService(AlumnoRepositoryImpl(db))
    return service.registrar_alumno(Alumno(**alumno.dict()))
