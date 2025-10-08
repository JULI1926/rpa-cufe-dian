"""
Rutas de Health Check y Sistema - RPA DIAN API
Contiene las rutas básicas de verificación de estado del servicio
"""

from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel, Field

# Crear router para rutas de health/sistema
router = APIRouter()

# Modelos Pydantic para responses
class ResponseBase(BaseModel):
    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)

@router.get("/", 
         summary="Redirigir a documentación",
         description="Ruta raíz que redirige a la documentación Swagger")
async def root():
    """Ruta raíz del API"""
    return {"message": "RPA DIAN API", "docs": "/docs", "redoc": "/redoc"}

@router.get("/health", 
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