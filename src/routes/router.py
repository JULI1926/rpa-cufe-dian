"""
Router Principal - RPA DIAN API
Agrupa todos los routers de la aplicación
"""

from fastapi import APIRouter
from . import health, dian

# Crear router principal
router = APIRouter()

# Incluir routers específicos
router.include_router(health.router)  # Rutas: /, /health
router.include_router(dian.router)    # Rutas: /api/v1/dian/*