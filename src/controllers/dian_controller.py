"""
Controlador DIAN - FastAPI
Maneja las operaciones relacionadas con el procesamiento RPA DIAN
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Import directo del orquestador usando ruta absoluta desde src
from src.orchestrators.orquestador_neek import main as ejecutar_orquestador

logger = logging.getLogger(__name__)

class DianController:
    """Controlador para operaciones DIAN"""
    
    async def procesar_facturas(self):
        """
        Ejecutar el orquestador DIAN       
        
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            logger.info("🚀 Iniciando procesamiento DIAN...")
            

            # Llamar directamente al orquestador
            resultado = ejecutar_orquestador()
            
            logger.info("✅ Procesamiento DIAN completado exitosamente")
            
            if resultado == 0:
                return {
                    "success": True,
                    "message": "Procesamiento DIAN completado exitosamente",
                    "resultado": resultado,
                    "timestamp": datetime.now()
                }
            else:
                return {
                    "success": False,
                    "message": "Error en el procesamiento DIAN",
                    "error": f"Orquestador retornó código: {resultado}",
                    "resultado": resultado,
                    "timestamp": datetime.now()
                }

        except Exception as e:
            logger.error(f"❌ Error en procesarFacturas: {e}")
            return {
                "success": False,
                "message": "Error interno en el procesamiento",
                "error": str(e),
                "timestamp": datetime.now()
            }