#!/usr/bin/env python3
"""
Script para ejecutar el servidor RPA DIAN API
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    # Agregar el directorio actual al path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Iniciando servidor RPA DIAN API...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("📖 Documentación alternativa en: http://localhost:8000/redoc")
    print("❤️  Health check en: http://localhost:8000/health")
    print("🔧 Configuración actual: config/VariablesGlobales.json")
    print("")
    print("Para detener el servidor presiona Ctrl+C")
    
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)