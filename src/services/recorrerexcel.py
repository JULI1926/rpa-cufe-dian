import sys
import os
import json
from datetime import datetime
import getpass

# Agregar el directorio padre al path para importar navegaciondian
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from navegaciondian import procesarfactura 
from utils.path_utils import get_config_path, get_logs_dir
from gateways.ApiDianGateway import get_facturas_faltantes

usuario = getpass.getuser()
print("Usuario del equipo:", usuario)

rutajson = get_config_path()
with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

primer_objeto = datos[0]

session_id = datetime.now().strftime('%Y%m%d%H%M%S')

base_logs = get_logs_dir()
os.makedirs(base_logs, exist_ok=True)
logeventos = os.path.join(base_logs, f"LogEventos-{session_id}.txt")
logerrores = os.path.join(base_logs, f"LogErrores-{session_id}.txt")

print("[INFO] Consultando facturas faltantes desde el endpoint...")

try:
    facturas_response = get_facturas_faltantes()
    
    if not facturas_response:
        print("[ERROR] No se pudo obtener respuesta del endpoint")
        sys.exit(1)
    
    # Verificar estructura de respuesta
    if facturas_response.get('status') != 200:
        print(f"[ERROR] Respuesta del endpoint con status {facturas_response.get('status')}")
        print(f"Mensaje: {facturas_response.get('message', 'Sin mensaje')}")
        sys.exit(1)
    
    # Extraer los registros
    response_data = facturas_response.get('response', {})
    records = response_data.get('records', [])
    total_missing = response_data.get('totalMissing', 0)
    
    print(f"[SUCCESS] Facturas faltantes obtenidas: {total_missing} registros")
    print(f"[INFO] Registros a procesar: {len(records)}")
    
    if len(records) == 0:
        print("[SUCCESS] No hay facturas faltantes para procesar")
        sys.exit(0)
        
except Exception as e:
    print(f"[ERROR] al consultar endpoint: {e}")
    sys.exit(1)

print("[INFO] Iniciando procesamiento de facturas faltantes...")

# Recorrer los registros del endpoint y procesar cada CUFE
for index, registro in enumerate(records):
    cufe = registro.get('cufeCude', '')
    batch = registro.get('batch', '')
    client_name = registro.get('clientName', '')
    client_document = registro.get('clientDocument', '')
    
    if not cufe:
        print(f"[WARNING] Registro {index + 1}: CUFE vacio, saltando...")
        continue
    
    print(f"[PROCESSING] Registro {index + 1}/{len(records)}: CUFE: {cufe[:20]}... Cliente: {client_name}")
    
    if client_name and client_document:
        print(f"[INFO] Usando datos del cliente desde endpoint: {client_name} ({client_document})")
    
    resultado = procesarfactura(cufe, batch, logeventos, logerrores, client_name, client_document)
    
    if not resultado:
        # Registrar en log de errores que la navegación falló para este CUFE
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Falló procesar CUFE: {cufe} | Batch: {batch}\n"
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        print(f"[ERROR] Registro {index + 1} -> CUFE: {cufe[:20]}... (ERROR: imagen no encontrada o navegacion fallida)")
        os.system("taskkill /f /im chrome.exe")
        continue
    
    print(f"[SUCCESS] Registro {index + 1} -> CUFE: {cufe[:20]}... procesado exitosamente")
    os.system("taskkill /f /im chrome.exe")

fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
mensaje = f"FECHA: [{fecha_actual}] | INFO | Fin Procesar Facturas Endpoint | Finalizo tarea | Finalizo con exito! Total procesadas: {len(records)}\n"
with open(logeventos, "a", encoding="utf-8") as archivo:
    archivo.write(mensaje)
    
print("[SUCCESS] Procesamiento completado - Facturas obtenidas desde endpoint")
print(f"[INFO] Total de registros procesados: {len(records)}")