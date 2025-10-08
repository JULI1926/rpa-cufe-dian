"""
Rutas DIAN - RPA DIAN API
Contiene todas las rutas relacionadas con el procesamiento RPA DIAN
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os
import sys

# Añadir el directorio src al path para importar los controladores
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from controllers.dian_controller import DianController

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para rutas de DIAN
router = APIRouter(
    prefix="/api/v1/dian",
    tags=["DIAN"]
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

class EstadoResponse(ResponseBase):
    estado: str
    archivos: Dict[str, Any]
    configuracion: Optional[Dict[str, Any]] = None

# Instanciar controlador
dian_controller = DianController()

@router.post("/procesar", 
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
          """)
async def procesar_facturas(request: ProcesarRequest):
    """Ejecutar el orquestador DIAN para procesar facturas"""
    try:
        result = await dian_controller.procesar_facturas(request.path_json)
        return result
    except Exception as e:
        logger.error(f"Error en procesar_facturas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estado",
         response_model=EstadoResponse,
         summary="Estado del sistema",
         description="""
         Verifica el estado de los archivos críticos y la configuración del sistema:
         
         - Scripts Python principales (orquestador, navegación, Excel)
         - Archivo de configuración VariablesGlobales.json
         - Configuración actual (sin datos sensibles como contraseñas)
         """)
async def obtener_estado():
    """Obtener estado del sistema RPA DIAN"""
    try:
        result = await dian_controller.obtener_estado()
        return result
    except Exception as e:
        logger.error(f"Error en obtener_estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))