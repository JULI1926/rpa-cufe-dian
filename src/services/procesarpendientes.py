import sys
import os
import json
from datetime import datetime
import getpass
import time

# Agregar el directorio padre al path para importar navegaciondian
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from navegaciondian import procesarfactura 
from gateways.ApiDianGateway import get_factura_faltante_siguiente

def procesar_pendientes_endpoint(lote):
    """
    Procesa facturas pendientes obtenidas desde el endpoint /facturas/faltantes/siguiente una por una.
    Si no hay más facturas, espera 30 minutos y vuelve a verificar.
    Args:
        lote (str): Identificador del lote de procesamiento (usado para logs)
    Returns:
        int: 0 si fue exitoso, 1 si hubo errores (pero ahora es un bucle infinito)
    """
    usuario = getpass.getuser()
    print(f"[INFO] Iniciando procesamiento continuo de facturas - Lote: {lote}")
    print(f"[INFO] Usuario del equipo: {usuario}")

    # Configurar rutas de logs
    base_logs = f"C:/Users/{usuario}/Documents/Archivos DIAN/"
    os.makedirs(base_logs, exist_ok=True)
    logeventos = os.path.join(base_logs, f"LogEventos-{lote}.txt")
    logerrores = os.path.join(base_logs, f"LogErrores-{lote}.txt")

    print("[INFO] Iniciando procesamiento continuo de facturas faltantes...")

    total_procesadas = 0

    while True:
        print("[INFO] Consultando siguiente factura pendiente...")

        try:
            factura_response = get_factura_faltante_siguiente()
            
            if not factura_response:
                print("[ERROR] No se pudo obtener respuesta del endpoint")
                print("[INFO] Esperando 30 minutos antes de reintentar...")
                time.sleep(1800)  # 30 minutos
                continue
            
            # Verificar estructura de respuesta
            if factura_response.get('status') != 200:
                print(f"[WARNING] No hay más facturas pendientes. Status: {factura_response.get('status')}")
                print(f"Mensaje: {factura_response.get('message', 'Sin mensaje')}")
                print("[INFO] Esperando 30 minutos antes de verificar nuevamente...")
                time.sleep(1800)  # 30 minutos
                continue
            
            # Extraer el registro
            registro = factura_response.get('response', {})
            cufe = registro.get('cufeCude', '')
            batch = registro.get('batch', '')
            client_name = registro.get('clientName', '')
            client_document = registro.get('clientDocument', '')

            if not cufe:
                print("[WARNING] Registro con CUFE vacío, saltando...")
                continue

            print(f"[PROCESSING] Procesando factura: CUFE: {cufe[:20]}... Cliente: {client_name}")

            resultado = procesarfactura(cufe, batch, logeventos, logerrores, client_name, client_document)

            if not resultado:
                fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
                mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Falló procesar CUFE: {cufe} | Batch: {batch}\n"
                with open(logerrores, "a", encoding="utf-8") as archivo:
                    archivo.write(mensajeerror)
                print(f"[ERROR] Falló procesar CUFE: {cufe[:20]}... (ERROR: imagen no encontrada o navegación fallida)")
                os.system("taskkill /f /im chrome.exe")
                continue

            total_procesadas += 1
            print(f"[SUCCESS] Factura procesada exitosamente. Total procesadas: {total_procesadas}")
            os.system("taskkill /f /im chrome.exe")

        except Exception as e:
            print(f"[ERROR] Error en el procesamiento: {e}")
            print("[INFO] Esperando 30 minutos antes de reintentar...")
            time.sleep(1800)  # 30 minutos
            continue

# Alias para compatibilidad

def ejecutar(lote):
    """Alias para mantener compatibilidad con llamadas existentes"""
    return procesar_pendientes_endpoint(lote)
