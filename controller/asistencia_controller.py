from datetime import datetime, timedelta
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from database.database import get_db
from sqlalchemy import func
from models.schemas import AsistenciaSchema
from repository.asistencia_repository import AsistenciaRepositoryImpl
from service.asistencia_service import AsistenciaService
from models.models import Asistencia, Alumno, Maestro

router = APIRouter()


@router.post("/entrada", response_model=AsistenciaSchema)
def registrar_entrada(persona_id: str, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar asistencia")

    # 🔹 Buscar si el usuario tiene una asistencia sin salida
    asistencia_pendiente = db.query(Asistencia).filter(
        Asistencia.persona_id == persona_id,
        Asistencia.fecha_salida == None  # Filtramos si no tiene salida
    ).first()

    if asistencia_pendiente:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene una asistencia activa sin salida registrada."
        )

    # 🔹 Buscar si es alumno o maestro
    alumno = db.query(Alumno).filter(Alumno.matricula == persona_id).first()
    if alumno:
        tipo_persona = "alumno"
    else:
        maestro = db.query(Maestro).filter(Maestro.numero_plaza == persona_id).first()
        if maestro:
            tipo_persona = "maestro"
        else:
            raise HTTPException(status_code=404, detail="Persona no encontrada en alumnos o maestros")

    # 🔹 Obtener la hora actual en GMT-6
    hora_actual = datetime.utcnow() - timedelta(hours=6)

    # 🔹 Registrar la asistencia
    service = AsistenciaService(AsistenciaRepositoryImpl(db))
    nueva_asistencia = service.registrar_entrada(persona_id=persona_id, tipo_persona=tipo_persona,
                                                 fecha_entrada=hora_actual)

    return nueva_asistencia


@router.post("/salida", response_model=AsistenciaSchema)
def registrar_salida(persona_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar salida")

    service = AsistenciaService(AsistenciaRepositoryImpl(db))
    asistencia = service.registrar_salida(persona_id)

    if not asistencia:
        raise HTTPException(status_code=404, detail="No se encontró asistencia registrada para esta persona")

    return asistencia


@router.get("/buscar/{persona_id}", response_model=AsistenciaSchema)
def buscar_asistencia(persona_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para consultar asistencia")

    service = AsistenciaService(AsistenciaRepositoryImpl(db))
    asistencia = service.buscar_asistencia(persona_id)

    if not asistencia:
        raise HTTPException(status_code=404, detail="No se encontró asistencia registrada para esta persona")

    return asistencia


# 1️⃣ 📊 Reporte por día y carrera
@router.get("/reporte/dia-carrera")
def reporte_asistencia_dia_carrera(
        fecha: datetime = Query(..., description="Formato: YYYY-MM-DD"),
        carrera: str = Query(..., description="Nombre de la carrera"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    fecha_inicio = fecha.replace(hour=0, minute=0, second=0)
    fecha_fin = fecha.replace(hour=23, minute=59, second=59)

    total_asistentes = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin,
        Alumno.carrera == carrera
    ).scalar()

    return {"fecha": fecha.strftime("%Y-%m-%d"), "carrera": carrera, "total_asistentes": total_asistentes}


# 2️⃣ Reporte total de asistencia por carrera
@router.get("/reporte/total-carrera")
def reporte_total_asistencia_carrera(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    resultados = db.query(
        Alumno.carrera, func.count(func.distinct(Asistencia.persona_id))
    ).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).group_by(
        Alumno.carrera
    ).all()

    return [{"carrera": carrera, "total_asistentes": total} for carrera, total in resultados]


# 3️⃣ 📊 Reporte de asistencia general por día
@router.get("/reporte/dia-general")
def reporte_asistencia_dia_general(
        fecha: datetime = Query(..., description="Formato: YYYY-MM-DD"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    fecha_inicio = fecha.replace(hour=0, minute=0, second=0)
    fecha_fin = fecha.replace(hour=23, minute=59, second=59)

    total_asistentes = db.query(func.count(func.distinct(Asistencia.persona_id))).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    return {"fecha": fecha.strftime("%Y-%m-%d"), "total_asistentes": total_asistentes}


# 4️⃣ 📊 Reporte de asistencia total en los 3 días (Alumnos y Maestros)
@router.get("/reporte/general-3dias")
def reporte_asistencia_3dias(
        fecha_inicio: datetime = Query(..., description="Inicio del evento YYYY-MM-DD"),
        fecha_fin: datetime = Query(..., description="Fin del evento YYYY-MM-DD"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0)
    fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)

    total_alumnos = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    total_maestros = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Maestro, Maestro.numero_plaza == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    return {
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
        "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
        "total_alumnos": total_alumnos,
        "total_maestros": total_maestros
    }


# 5️⃣ 📊 Reporte de asistencia por género (Hombres y Mujeres)
@router.get("/reporte/genero")
def reporte_asistencia_genero(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    hombres = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Alumno.genero == "Masculino"
    ).scalar()

    mujeres = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Alumno.genero == "Femenino"
    ).scalar()

    return {"total_hombres": hombres, "total_mujeres": mujeres}


# 6️⃣ 📊 Asistentes en tiempo real (Día actual por carrera)
@router.get("/reporte/tiempo-real")
def asistentes_tiempo_real(
        carrera: str = Query(None, description="Filtrar por carrera (Opcional)"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    hoy = datetime.utcnow() - timedelta(hours=6)
    fecha_inicio = hoy.replace(hour=0, minute=0, second=0)
    fecha_fin = hoy.replace(hour=23, minute=59, second=59)

    query = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    )

    if carrera:
        query = query.filter(Alumno.carrera == carrera)

    asistentes = query.scalar()

    return {
        "fecha": hoy.strftime("%Y-%m-%d"),
        "carrera": carrera if carrera else "Todas",
        "total_asistentes": asistentes
    }
