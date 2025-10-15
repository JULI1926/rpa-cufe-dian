"""
Modelos Pydantic (Schemas) para la API.
Define la estructura de los datos para las peticiones y respuestas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProcesarRequest(BaseModel):
    """Modelo para la petición del endpoint de procesamiento."""
    path_json: Optional[str] = Field(
        default=None,
        title="Ruta al archivo JSON de configuración",
        description="Ruta opcional a un archivo de configuración 'VariablesGlobales.json'. Si no se provee, se usará el archivo por defecto en 'config/VariablesGlobales.json'."
    )

class ResponseBase(BaseModel):
    """Modelo base para las respuestas."""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)

class ProcesarResponse(ResponseBase):
    """Modelo para la respuesta del endpoint de procesamiento."""
    message: str
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None
    stderr: Optional[str] = None
