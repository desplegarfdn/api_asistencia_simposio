from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import create_tables
from controller import asistencia_controller, alumos_controller, maestros_controller, usuario_controller, \
    auth_controller, log_controller

origins = ["*"]

app = FastAPI(title="API de Asistencia",
              version="1.0",
              description="Esta es una API para gestionar asistencias del simposio",
            )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(asistencia_controller.router, prefix="/asistencia", tags=["asistencia"])
app.include_router(alumos_controller.router, prefix="/alumnos", tags=["alumnos"])
app.include_router(maestros_controller.router, prefix="/maestros", tags=["maestros"])
app.include_router(usuario_controller.router, prefix="/usuarios", tags=["usuarios"])
app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
app.include_router(log_controller.router, prefix="/logs", tags=["logs"])
@app.on_event("startup")
def startup_event():
    create_tables()
