import sys
import os

# Agregar el directorio padre al path para importar navegaciondian
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from navegaciondian import procesarfactura 
# Importar utilidades de rutas
sys.path.append(os.path.dirname(current_dir))
from utils.path_utils import get_config_path, get_absolute_path, get_logs_dir
from gateways.ApiDianGateway import get_facturas_faltantes
import json
from datetime import datetime
import getpass

usuario = getpass.getuser()
print("Usuario del equipo:", usuario)

#TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON (opcional)
if len(sys.argv) > 1:
    lote = os.path.abspath(sys.argv[1])
    # Si el argumento viene como una ruta (por ejemplo inyectada por un runner), tomar solo el nombre final
    try:
        lote = os.path.basename(lote)
    except Exception:
        pass
else:
    # Permitir ejecutar el script directamente para pruebas: generar lote por timestamp
    from datetime import datetime as _dt
    lote = _dt.now().strftime('%Y%m%d%H%M%S')
    print(f'No se proporcionó argumento lote; usando lote por defecto: {lote}')

# #TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON
# parametros = os.path.abspath(sys.argv[1])

# #SEPARAMOS LA CADENA
# cadena=parametros.split('=')

# #SEPARAMOS LA CADENA POR POSICIONES
# #carpeta=cadena[0]
# rutajson=cadena[0]
# loop=cadena[1]

# Obtener la fecha actual en formato YYYYMMDD
fecha_actual = datetime.now().strftime('%Y%m%d')

# Leer el archivo JSON usando utilidades de rutas
rutajson = get_config_path()

with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

# Asignar los valores a variables (solo las que necesitamos para logs)
documento = primer_objeto['documentocliente']



# RUTA LOGS: usar utilidades de rutas para la carpeta de logs
base_logs = get_logs_dir()
os.makedirs(base_logs, exist_ok=True)
logeventos = os.path.join(base_logs, f"LogEventos-{documento}{lote}.txt")
logerrores = os.path.join(base_logs, f"LogErrores-{documento}{lote}.txt")

# ===============================================
# OBTENER FACTURAS FALTANTES DESDE ENDPOINT
# ===============================================
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

# ===============================================
# PROCESAR FACTURAS FALTANTES
# ===============================================
print("[INFO] Iniciando procesamiento de facturas faltantes...")

# Recorrer los registros del endpoint y procesar cada CUFE
for index, registro in enumerate(records):
    cufe = registro.get('cufeCude', '')
    batch = registro.get('batch', '')
    
    if not cufe:
        print(f"[WARNING] Registro {index + 1}: CUFE vacio, saltando...")
        continue
    
    print(f"[PROCESSING] Registro {index + 1}/{len(records)}: CUFE: {cufe[:20]}... Batch: {batch}")
    
    # Llamar a la función de procesamiento
    resultado = procesarfactura(cufe, lote, logeventos, logerrores)
    
    if not resultado:
        # Registrar en log de errores que la navegación falló para este CUFE
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Falló procesar CUFE: {cufe} | Lote: {lote} | Batch: {batch}\n"
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        print(f"[ERROR] Registro {index + 1} -> CUFE: {cufe[:20]}... (ERROR: imagen no encontrada o navegacion fallida)")
        # Asegurarse de cerrar chrome por si queda abierto
        os.system("taskkill /f /im chrome.exe")
        # Continuar con la siguiente fila
        continue
    
    print(f"[SUCCESS] Registro {index + 1} -> CUFE: {cufe[:20]}... procesado exitosamente")
    # Cierra todos los procesos de Google Chrome (post éxito)
    os.system("taskkill /f /im chrome.exe")


# Obtener la fecha y hora actual en el formato deseado
fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
# Crear el mensaje de log
mensaje = f"FECHA: [{fecha_actual}] | INFO | Fin Procesar Facturas Endpoint | Finalizo tarea | Finalizo con exito! Total procesadas: {len(records)}\n"
# Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
with open(logeventos, "a", encoding="utf-8") as archivo:
    archivo.write(mensaje)
    
print("[SUCCESS] Procesamiento completado - Facturas obtenidas desde endpoint")
print(f"[INFO] Total de registros procesados: {len(records)}")