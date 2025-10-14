import sys
import os
import json
import time
import random
from datetime import datetime
import getpass

# Agregar el directorio padre al path para importar navegaciondian
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from navegaciondian import procesarfactura 
from gateways.ApiDianGateway import get_facturas_faltantes


def retry_with_backoff(func, max_retries=3, base_delay=5, max_delay=60, backoff_factor=2):
    """
    Ejecuta una función con reintentos y backoff exponencial
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
        backoff_factor: Factor de multiplicación para el backoff
    
    Returns:
        Resultado de la función o None si todos los reintentos fallan
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 para el intento inicial
        try:
            print(f"[RETRY] Intento {attempt + 1}/{max_retries + 1}")
            result = func()
            
            if result is not None and result != False:
                if attempt > 0:
                    print(f"[RETRY] Éxito en intento {attempt + 1}")
                return result
            else:
                print(f"[RETRY] Función retornó None/False en intento {attempt + 1}")
                if attempt == max_retries:
                    return None
                last_exception = Exception("Función retornó None/False")
                
        except Exception as e:
            print(f"[RETRY] Error en intento {attempt + 1}: {str(e)}")
            last_exception = e
            
            if attempt == max_retries:
                print(f"[RETRY] Todos los reintentos agotados. Último error: {str(e)}")
                return None
        
        # Calcular delay con backoff exponencial y jitter
        if attempt < max_retries:
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
            jitter = random.uniform(0.1, 1.0) * delay * 0.1  # 10% de jitter
            total_delay = delay + jitter
            
            print(f"[RETRY] Esperando {total_delay:.1f} segundos antes del siguiente intento...")
            time.sleep(total_delay)
    
    return None


def save_processing_state(lote, processed_cufes, failed_cufes, in_progress_cufe=None):
    """
    Guarda el estado actual del procesamiento para recuperación
    
    Args:
        lote: Identificador del lote
        processed_cufes: Lista de CUFE procesados exitosamente
        failed_cufes: Lista de CUFE que fallaron definitivamente
        in_progress_cufe: CUFE actualmente en proceso (opcional)
    """
    try:
        usuario = getpass.getuser()
        state_dir = f"C:/Users/{usuario}/Documents/Archivos DIAN/"
        os.makedirs(state_dir, exist_ok=True)
        
        state_file = os.path.join(state_dir, f"estado_procesamiento_{lote}.json")
        
        state = {
            "lote": lote,
            "timestamp": datetime.now().isoformat(),
            "processed_cufes": processed_cufes,
            "failed_cufes": failed_cufes,
            "in_progress_cufe": in_progress_cufe,
            "total_processed": len(processed_cufes),
            "total_failed": len(failed_cufes)
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"[STATE] Estado guardado: {len(processed_cufes)} procesados, {len(failed_cufes)} fallidos")
        
    except Exception as e:
        print(f"[WARNING] No se pudo guardar estado: {e}")


def load_processing_state(lote):
    """
    Carga el estado guardado del procesamiento
    
    Args:
        lote: Identificador del lote
    
    Returns:
        dict con estado o None si no existe
    """
    try:
        usuario = getpass.getuser()
        state_dir = f"C:/Users/{usuario}/Documents/Archivos DIAN/"
        state_file = os.path.join(state_dir, f"estado_procesamiento_{lote}.json")
        
        if not os.path.exists(state_file):
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print(f"[STATE] Estado cargado: {state.get('total_processed', 0)} procesados, {state.get('total_failed', 0)} fallidos")
        return state
        
    except Exception as e:
        print(f"[WARNING] No se pudo cargar estado: {e}")
        return None


def is_recoverable_error(error_msg):
    """
    Determina si un error es recuperable (merece reintento)
    
    Args:
        error_msg: Mensaje de error
    
    Returns:
        bool: True si es recuperable
    """
    recoverable_patterns = [
        "session deleted",  # Navegador cerrado
        "invalid session id",  # Sesión perdida
        "chrome crashed",  # Chrome se cerró
        "connection refused",  # Problemas de conexión
        "timeout",  # Timeouts
        "net::ERR",  # Errores de red
        "no such window",  # Ventana cerrada
        "element not found",  # Elementos no encontrados (temporal)
        "stale element",  # Elementos obsoletos
    ]
    
    error_lower = str(error_msg).lower()
    return any(pattern in error_lower for pattern in recoverable_patterns)

def procesar_pendientes_endpoint(lote):
    """
    Procesa facturas pendientes obtenidas desde el endpoint (no desde Excel)
    Incluye reintentos automáticos y recuperación de estado
    
    Args:
        lote (str): Identificador del lote de procesamiento
    Returns:
        int: 0 si fue exitoso, 1 si hubo errores
    """
    usuario = getpass.getuser()
    print(f"[INFO] Iniciando procesamiento de facturas - Lote: {lote}")
    print(f"[INFO] Usuario del equipo: {usuario}")

    # Configurar rutas de logs
    base_logs = f"C:/Users/{usuario}/Documents/Archivos DIAN/"
    os.makedirs(base_logs, exist_ok=True)
    logeventos = os.path.join(base_logs, f"LogEventos-{lote}.txt")
    logerrores = os.path.join(base_logs, f"LogErrores-{lote}.txt")

    # Intentar cargar estado anterior para recuperación
    estado_anterior = load_processing_state(lote)
    processed_cufes = estado_anterior.get('processed_cufes', []) if estado_anterior else []
    failed_cufes = estado_anterior.get('failed_cufes', []) if estado_anterior else []
    
    if estado_anterior:
        print(f"[RECOVERY] Recuperando procesamiento anterior: {len(processed_cufes)} procesados, {len(failed_cufes)} fallidos")

    print("[INFO] Consultando facturas pendientes desde el endpoint...")

    try:
        facturas_response = get_facturas_faltantes()
        
        if not facturas_response:
            print("[ERROR] No se pudo obtener respuesta del endpoint")
            return 1
        
        # Verificar estructura de respuesta
        if facturas_response.get('status') != 200:
            print(f"[ERROR] Respuesta del endpoint con status {facturas_response.get('status')}")
            print(f"Mensaje: {facturas_response.get('message', 'Sin mensaje')}")
            return 1
        
        # Extraer los registros
        response_data = facturas_response.get('response', {})
        records = response_data.get('records', [])
        total_missing = response_data.get('totalMissing', 0)
        
        print(f"[SUCCESS] Facturas faltantes obtenidas: {total_missing} registros")
        print(f"[INFO] Registros a procesar: {len(records)}")
        
        if len(records) == 0:
            print("[SUCCESS] No hay facturas faltantes para procesar")
            return 0
            
    except Exception as e:
        print(f"[ERROR] al consultar endpoint: {e}")
        return 1

    print("[INFO] Iniciando procesamiento de facturas faltantes...")

    # Filtrar registros que ya fueron procesados o fallaron definitivamente
    registros_pendientes = []
    for registro in records:
        cufe = registro.get('cufeCude', '')
        if cufe and cufe not in processed_cufes and cufe not in failed_cufes:
            registros_pendientes.append(registro)
    
    print(f"[INFO] Registros pendientes de procesar: {len(registros_pendientes)} (filtrados {len(records) - len(registros_pendientes)} ya procesados)")
    
    # Procesar cada registro pendiente con reintentos
    for index, registro in enumerate(registros_pendientes):
        cufe = registro.get('cufeCude', '')
        batch = registro.get('batch', '')
        client_name = registro.get('clientName', '')
        client_document = registro.get('clientDocument', '')

        if not cufe:
            print(f"[WARNING] Registro {index + 1}: CUFE vacío, saltando...")
            continue

        print(f"[PROCESSING] Registro {index + 1}/{len(registros_pendientes)}: CUFE: {cufe[:20]}... Cliente: {client_name}")
        
        # Marcar como en proceso antes de empezar
        save_processing_state(lote, processed_cufes, failed_cufes, cufe)
        
        # Función wrapper para el procesamiento con reintentos
        def attempt_process_factura():
            try:
                resultado = procesarfactura(cufe, batch, logeventos, logerrores, client_name, client_document)
                return resultado
            except Exception as e:
                print(f"[ERROR] Excepción durante procesamiento de CUFE {cufe}: {e}")
                # Determinar si es error recuperable
                if is_recoverable_error(str(e)):
                    print(f"[RETRY] Error recuperable detectado, permitiendo reintento")
                    return None  # Permitir reintento
                else:
                    print(f"[RETRY] Error no recuperable, cancelando reintentos")
                    raise e  # Error no recuperable, no reintentar
        
        # Ejecutar con reintentos
        resultado = retry_with_backoff(attempt_process_factura, max_retries=3, base_delay=10)
        
        if resultado:
            processed_cufes.append(cufe)
            print(f"[SUCCESS] Registro {index + 1} -> CUFE: {cufe[:20]}... procesado exitosamente")
        else:
            failed_cufes.append(cufe)
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            mensajeerror = f"FECHA: [{fecha_actual}] | ERROR | ErrorRegistroFactura | Falló procesar CUFE después de reintentos: {cufe} | Batch: {batch}\n"
            with open(logerrores, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
            print(f"[ERROR] Registro {index + 1} -> CUFE: {cufe[:20]}... (FALLÓ DEFINITIVAMENTE después de reintentos)")

        # Guardar estado después de cada factura
        save_processing_state(lote, processed_cufes, failed_cufes)
        
        # Limpiar procesos de Chrome entre facturas
        os.system("taskkill /f /im chrome.exe >nul 2>&1")
        os.system("taskkill /f /im msedge.exe >nul 2>&1")
        time.sleep(2)  # Breve pausa entre facturas

    # Resumen final
    total_procesadas = len(processed_cufes)
    total_fallidas = len(failed_cufes)
    total_original = len(records)
    
    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    mensaje = f"FECHA: [{fecha_actual}] | INFO | Fin Procesar Facturas Endpoint | Finalizo tarea | Procesadas: {total_procesadas} | Fallidas: {total_fallidas} | Total: {total_original}\n"
    
    with open(logeventos, "a", encoding="utf-8") as archivo:
        archivo.write(mensaje)
        
    print("[SUCCESS] Procesamiento completado - Facturas obtenidas desde endpoint")
    print(f"[SUMMARY] Total procesadas: {total_procesadas}, Fallidas: {total_fallidas}, Total: {total_original}")
    
    # Retornar éxito solo si no hay fallos definitivos
    return 0 if total_fallidas == 0 else 1

# Alias para compatibilidad

def ejecutar(lote):
    """Alias para mantener compatibilidad con llamadas existentes"""
    return procesar_pendientes_endpoint(lote)
