"""
RPA DIAN API - FastAPI Server
API REST para automatización RPA de validaciones DIAN con estructura FAZT API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import os
import subprocess
import sys
import json
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

# Modelos Pydantic
class ProcesarRequest(BaseModel):
    path_json: Optional[str] = Field(
        None, 
        description="Ruta personalizada al archivo VariablesGlobales.json (opcional)",
        example="C:/ruta/personalizada/VariablesGlobales.json"
    )

class ResponseBase(BaseModel):
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)

class ProcesarResponse(ResponseBase):
    message: str
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None
    stderr: Optional[str] = None

class ErrorResponse(ResponseBase):
    error: str
    details: Optional[str] = None

class EstadoResponse(ResponseBase):
    estado: str
    archivos: Dict[str, Any]
    configuracion: Optional[Dict[str, Any]] = None

# Importar controladores desde la nueva estructura
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.controllers.dian_controller import DianController

# Instanciar controlador
dian_controller = DianController()

# Rutas de la API
@app.get("/", 
         summary="Redirigir a documentación",
         description="Ruta raíz que redirige a la documentación Swagger")
async def root():
    return {"message": "RPA DIAN API", "docs": "/docs", "redoc": "/redoc"}

@app.get("/health", 
         response_model=ResponseBase,
         summary="Health Check",
         description="Verificar estado del servicio",
         tags=["Health"])
async def health_check():
    """Endpoint para verificar que el servicio está funcionando correctamente"""
    return ResponseBase(
        success=True,
        timestamp=datetime.now()
    )

@app.post("/api/v1/dian/procesar", 
          response_model=ProcesarResponse,
          summary="Procesar facturas DIAN",
          description="""
          Ejecuta el orquestador principal del RPA DIAN que:
          
          - Lee el archivo Excel con las facturas DIAN
          - Navega por cada factura usando Selenium
          - Valida CUFE/CUDE en la página de DIAN
          - Envía correos de notificación de inicio y fin
          - Genera logs de eventos y errores
          
          El proceso puede tomar varios minutos dependiendo del número de facturas.
          """,
          tags=["DIAN"])
async def procesar_facturas(request: ProcesarRequest):
    """Ejecutar el orquestador DIAN para procesar facturas"""
    try:
        result = await dian_controller.procesar_facturas(request.path_json)
        return result
    except Exception as e:
        logger.error(f"Error en procesar_facturas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dian/estado",
         response_model=EstadoResponse,
         summary="Estado del sistema",
         description="""
         Verifica el estado de los archivos críticos y la configuración del sistema:
         
         - Scripts Python principales (orquestador, navegación, Excel)
         - Archivo de configuración VariablesGlobales.json
         - Configuración actual (sin datos sensibles como contraseñas)
         """,
         tags=["DIAN"])
async def obtener_estado():
    """Obtener estado del sistema RPA DIAN"""
    try:
        result = await dian_controller.obtener_estado()
        return result
    except Exception as e:
        logger.error(f"Error en obtener_estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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