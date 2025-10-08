"""
RPA DIAN API - FastAPI Server
API REST para automatización RPA de validaciones DIAN con estructura FAZT API
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = FastAPI(
    title="RPA DIAN API",
    description="""
    API REST para automatización RPA de validaciones DIAN con estructura FAZT API
    
    ## Funcionalidades principales:
    
    * **Procesamiento DIAN**: Ejecuta el orquestador principal que procesa facturas DIAN
    * **Validación CUFE/CUDE**: Navega automáticamente por la página de DIAN
    * **Notificaciones**: Envía correos de inicio, fin y errores
    * **Logs**: Genera logs detallados de eventos y errores
    * **Estado del sistema**: Verifica archivos críticos y configuración
    
    ## Estructura del proyecto:
    
    * `src/controllers/`: Controladores HTTP
    * `src/orchestrators/`: Lógica de negocio y orquestación
    * `src/services/`: Servicios de procesamiento de datos
    * `src/gateways/`: Comunicación con APIs externas
    * `config/`: Archivos de configuración
    """,
    version="1.0.0",
    contact={
        "name": "CYT - Julia",
        "email": "soporteyawi@cyt.com.co"
    },
    license_info={
        "name": "MIT"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar las rutas desde la nueva estructura
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.routes import router

# Incluir todas las rutas desde el router centralizado
app.include_router(router)

# Manejo de errores globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "details": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    print("🚀 Iniciando servidor RPA DIAN API...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("❤️  Health check en: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )