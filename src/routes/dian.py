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
        None               
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

# Instanciar controlador
dian_controller = DianController()

@router.post("/procesar", 
          response_model=ProcesarResponse,
          summary="Procesar facturas DIAN",
          description="""
          Ejecuta el orquestador principal del RPA DIAN que:
          
          - Consulta facturas pendientes desde base de datos remota Azure
          - Navega por cada factura usando Selenium
          - Valida CUFE/CUDE en la página de DIAN
          - Envía correos de notificación de inicio y fin
          - Genera logs de eventos y errores
          
          El proceso puede tomar varios minutos dependiendo del número de facturas.
          """)
async def procesar_facturas(request: ProcesarRequest):
    """Ejecutar el orquestador DIAN para procesar facturas"""
    try:
        result = await dian_controller.procesar_facturas()
        return result
    except Exception as e:
        logger.error(f"Error en procesar_facturas: {e}")
        raise HTTPException(status_code=500, detail=str(e))