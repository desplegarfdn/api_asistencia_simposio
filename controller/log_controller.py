from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from repository.log_repository import LogRepositoryImpl
from service.log_service import LogService
from auth.auth import get_current_user
from typing import List, Dict

router = APIRouter()

@router.get("/contador", response_model=List[Dict[str, int]])
def obtener_contador_entradas_salidas(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para ver los logs")

    service = LogService(LogRepositoryImpl(db))
    return service.contar_registros_por_usuario()
