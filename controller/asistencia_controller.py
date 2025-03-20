from datetime import datetime, timedelta
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from database.database import get_db
from sqlalchemy import func
from models.schemas import AsistenciaSchema
from repository.asistencia_repository import AsistenciaRepositoryImpl
from repository.log_repository import LogRepositoryImpl
from service.asistencia_service import AsistenciaService
from models.models import Asistencia, Alumno, Maestro
from service.log_service import LogService

router = APIRouter()

@router.post("/entrada", response_model=dict)
def registrar_entrada(persona_id: str, db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar asistencia")

    asistencia_pendiente = db.query(Asistencia).filter(
        Asistencia.persona_id == persona_id,
        Asistencia.fecha_salida == None
    ).first()

    if asistencia_pendiente:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene una asistencia activa sin salida registrada."
        )

    alumno = db.query(Alumno).filter(Alumno.matricula == persona_id).first()
    if alumno:
        tipo_persona = "alumno"
        nombre_completo = f"{alumno.nombre} {alumno.apellido_p} {alumno.apellido_m}"
    else:
        maestro = db.query(Maestro).filter(Maestro.numero_plaza == persona_id).first()
        if maestro:
            tipo_persona = "maestro"
            nombre_completo = f"{maestro.nombre} {maestro.apellido_p} {maestro.apellido_m}"
        else:
            raise HTTPException(status_code=404, detail="Persona no encontrada en alumnos o maestros")

    hora_actual = datetime.utcnow() - timedelta(hours=6)

    service = AsistenciaService(AsistenciaRepositoryImpl(db))
    nueva_asistencia = service.registrar_entrada(persona_id=persona_id, tipo_persona=tipo_persona, fecha_entrada=hora_actual)

    # 🔹 Registrar log de actividad
    log_service = LogService(LogRepositoryImpl(db))
    log_service.registrar_log(
        usuario_id=current_user.id,
        username=current_user.username,
        endpoint="/entrada",
        metodo="POST",
        mensaje=f"Registró la entrada de ({persona_id})"
    )

    return {
        "id": nueva_asistencia.id,
        "persona_id": persona_id,
        "tipo_persona": tipo_persona,
        "nombre_completo": nombre_completo,
        "fecha_entrada": nueva_asistencia.fecha_entrada
    }


@router.post("/salida", response_model=dict)
def registrar_salida(persona_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para registrar salida")

    service = AsistenciaService(AsistenciaRepositoryImpl(db))
    asistencia = service.registrar_salida(persona_id)

    if not asistencia:
        raise HTTPException(status_code=404, detail="No se encontró asistencia registrada para esta persona")

    alumno = db.query(Alumno).filter(Alumno.matricula == persona_id).first()
    if alumno:
        nombre_completo = f"{alumno.nombre} {alumno.apellido_p} {alumno.apellido_m}"
    else:
        maestro = db.query(Maestro).filter(Maestro.numero_plaza == persona_id).first()
        if maestro:
            nombre_completo = f"{maestro.nombre} {maestro.apellido_p} {maestro.apellido_m}"
        else:
            raise HTTPException(status_code=404, detail="Persona no encontrada en alumnos o maestros")

    # 🔹 Registrar log de actividad
    log_service = LogService(LogRepositoryImpl(db))
    log_service = LogService(LogRepositoryImpl(db))
    log_service.registrar_log(
        usuario_id=current_user.id,
        username=current_user.username,
        endpoint="/salida",
        metodo="POST",
        mensaje=f"Registró la salida de ({persona_id})"
    )

    return {
        "id": asistencia.id,
        "persona_id": persona_id,
        "tipo_persona": asistencia.tipo_persona,
        "nombre_completo": nombre_completo,
        "fecha_salida": asistencia.fecha_salida
    }


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

@router.get("/reporte/genero/hoy")
def reporte_asistencia_genero_hoy(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    # Obtener la fecha actual en GMT-6
    hoy = datetime.utcnow() - timedelta(hours=6)
    fecha_inicio = hoy.replace(hour=0, minute=0, second=0)
    fecha_fin = hoy.replace(hour=23, minute=59, second=59)

    # Contar asistentes hombres del día actual
    hombres = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Alumno.genero == "Masculino",
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    # Contar asistentes mujeres del día actual
    mujeres = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Alumno.genero == "Femenino",
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    return {
        "fecha": hoy.strftime("%Y-%m-%d"),
        "total_hombres": hombres,
        "total_mujeres": mujeres
    }

@router.get("/reporte/total-carrera/hoy")
def reporte_total_asistencia_carrera_hoy(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    # Obtener la fecha actual en GMT-6
    hoy = datetime.utcnow() - timedelta(hours=6)
    fecha_inicio = hoy.replace(hour=0, minute=0, second=0)
    fecha_fin = hoy.replace(hour=23, minute=59, second=59)

    # Consulta para obtener asistencia del día actual agrupada por carrera
    resultados = db.query(
        Alumno.carrera,
        func.count(func.distinct(Asistencia.persona_id))
    ).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).group_by(
        Alumno.carrera
    ).all()

    return {
        "fecha": hoy.strftime("%Y-%m-%d"),
        "detalle": [{"carrera": carrera, "total_asistentes": total} for carrera, total in resultados]
    }

@router.get("/reporte/faltantes-salida")
def reporte_faltantes_salida(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    # Contar alumnos que no han registrado su salida
    total_faltantes = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_salida.is_(None)  # Filtra los que no tienen salida registrada
    ).scalar()

    return {
        "total_faltantes": total_faltantes
    }

@router.get("/reporte/faltantes-evento")
def reporte_faltantes_evento(
        fecha: datetime = Query(..., description="Formato: YYYY-MM-DD"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user.role not in ["admin", "capturista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver reportes")

    # Obtener la fecha exacta en GMT-6
    fecha_inicio = fecha.replace(hour=0, minute=0, second=0)
    fecha_fin = fecha.replace(hour=23, minute=59, second=59)

    # Contar el total de alumnos registrados en la base de datos
    total_alumnos = db.query(func.count(Alumno.matricula)).scalar()

    # Contar el número de alumnos que asistieron ese día
    total_asistentes = db.query(func.count(func.distinct(Asistencia.persona_id))).join(
        Alumno, Alumno.matricula == Asistencia.persona_id
    ).filter(
        Asistencia.fecha_entrada >= fecha_inicio,
        Asistencia.fecha_entrada <= fecha_fin
    ).scalar()

    # Calcular los alumnos que faltaron
    total_faltantes = total_alumnos - total_asistentes

    return {
        "fecha": fecha.strftime("%Y-%m-%d"),
        "total_alumnos": total_alumnos,
        "total_asistentes": total_asistentes,
        "total_faltantes": total_faltantes
    }
