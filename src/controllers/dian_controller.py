"""
Controlador DIAN - FastAPI
Maneja las operaciones relacionadas con el procesamiento RPA DIAN
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DianController:
    """Controlador para operaciones DIAN"""
    
    def __init__(self):
        """Inicializar controlador"""
        # Obtener la ruta base del proyecto (desde src/controllers/ subir dos niveles)
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
    async def procesar_facturas(self, path_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecutar el orquestador DIAN
        
        Args:
            path_json: Ruta personalizada al archivo VariablesGlobales.json
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # Ruta al script orquestador
            orchestrator_path = os.path.join(
                self.base_path, 
                'src', 
                'orchestrators', 
                'orquestador_neek.py'
            )
            
            # Verificar que el archivo existe
            if not os.path.exists(orchestrator_path):
                raise FileNotFoundError(f"Script orquestador no encontrado en: {orchestrator_path}")

            logger.info("🚀 Iniciando procesamiento DIAN...")
            logger.info(f"📁 Script: {orchestrator_path}")
            if path_json:
                logger.info(f"🔧 Config personalizada: {path_json}")

            # Preparar comando Python
            cmd = [sys.executable, orchestrator_path]
            if path_json:
                cmd.append(path_json)

            # Ejecutar el script Python
            logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(orchestrator_path),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora máximo
            )

            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            logger.info(f"✅ Proceso finalizado con código: {result.returncode}")
            
            if stdout:
                logger.info(f"🐍 Python stdout: {stdout}")
            if stderr:
                logger.warning(f"⚠️  Python stderr: {stderr}")

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Procesamiento DIAN completado exitosamente",
                    "exit_code": result.returncode,
                    "output": stdout,
                    "timestamp": datetime.now()
                }
            else:
                return {
                    "success": False,
                    "message": "Error en el procesamiento DIAN",
                    "error": "Error en el procesamiento DIAN",
                    "exit_code": result.returncode,
                    "output": stdout,
                    "stderr": stderr,
                    "timestamp": datetime.now()
                }

        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout ejecutando el script Python")
            return {
                "success": False,
                "message": "Timeout en el procesamiento",
                "error": "Timeout ejecutando el script Python (más de 1 hora)",
                "timestamp": datetime.now()
            }
        except FileNotFoundError as e:
            logger.error(f"❌ Archivo no encontrado: {e}")
            return {
                "success": False,
                "message": "Archivo orquestador no encontrado",
                "error": "Script orquestador no encontrado",
                "details": str(e),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"❌ Error en procesarFacturas: {e}")
            return {
                "success": False,
                "message": "Error interno en el procesamiento",
                "error": "Error interno del servidor",
                "details": str(e),
                "timestamp": datetime.now()
            }

    async def obtener_estado(self) -> Dict[str, Any]:
        """
        Obtener estado del sistema
        
        Returns:
            Dict con estado del sistema
        """
        try:
            config_path = os.path.join(self.base_path, 'config', 'VariablesGlobales.json')
            
            # Verificar archivos críticos
            archivos = {
                "orquestador": os.path.join(self.base_path, 'src', 'orchestrators', 'orquestador_neek.py'),
                "navegacion": os.path.join(self.base_path, 'src', 'services', 'navegaciondian.py'),
                "recorrer_excel": os.path.join(self.base_path, 'src', 'services', 'recorrerexcel.py'),
                "config": config_path
            }

            estado_archivos = {}
            for nombre, ruta in archivos.items():
                estado_archivos[nombre] = {
                    "existe": os.path.exists(ruta),
                    "ruta": ruta
                }

            # Leer configuración si existe
            configuracion = None
            if estado_archivos["config"]["existe"]:
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        configuracion = config_data[0] if config_data else {}
                        
                        # Ocultar información sensible
                        if configuracion and "contrasenarpa" in configuracion:
                            configuracion["contrasenarpa"] = "***hidden***"
                            
                except Exception as config_error:
                    logger.error(f"Error leyendo configuración: {config_error}")
                    configuracion = {"error": "No se pudo leer la configuración"}

            return {
                "success": True,
                "estado": "Sistema operativo",
                "archivos": estado_archivos,
                "configuracion": configuracion,
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estado: {e}")
            return {
                "success": False,
                "error": "Error obteniendo estado del sistema",
                "details": str(e),
                "timestamp": datetime.now()
            }