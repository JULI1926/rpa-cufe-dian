import os
import os
import json
from datetime import datetime
from src.services.procesarpendientes import procesar_pendientes_endpoint
from src.gateways.iniciocorreo import main as enviar_inicio
from src.gateways.fincorreo import main as enviar_fin
from src.gateways.enviocorreogmailerror import main as enviar_error

def enviar_correo_inicio(rutajson):
    # Llamada directa a la función de envío de correo de inicio
    try:
        enviar_inicio(rutajson)
    except Exception as e:
        print('Warning: envío correo inicio falló', e)


def enviar_correo_fin(lote):
    try:
        # Llamada directa a la función de envío de correo de fin
        enviar_fin(lote)
    except Exception as e:
        print('Warning: envío correo fin falló', e)


def enviar_correo_error(rutajson, cuerpo):
    try:
        # Llamada directa a la función de envío de correo de error
        param = f"{rutajson}={cuerpo}"
        enviar_error(param)
    except Exception as e:
        print('Warning: envío correo error falló', e)


def main(path_json=None):
    # Leer variables directamente del JSON fijo
    config_path = path_json if path_json and os.path.isfile(path_json) else "./config/VariablesGlobales.json"
    
    print(f"[DEBUG] Cargando configuración desde: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        vars_obj = data[0]
        print(f"[SUCCESS] Configuración cargada exitosamente")
    except Exception as e:
        print(f"[ERROR] No se pudo cargar la configuración: {e}")
        return 1

    # Generar lote con fecha y hora compacta
    now = datetime.now()
    lote = now.strftime('%Y%m%d%H%M%S')
    print(f'[OK] Lote generado: {lote}')

    # Enviar correo de inicio (intento, no bloquear si falla)
    enviar_correo_inicio(config_path)

    # Llamar directamente al procesador de facturas
    try:
        resultado = procesar_pendientes_endpoint(lote)
        if resultado != 0:
            raise Exception(f"Error en procesar_pendientes_endpoint: código {resultado}")
    except Exception as e:
        cuerpo = f'Error al ejecutar procesarpendientes: {str(e)}'
        print(cuerpo)
        enviar_correo_error(config_path, cuerpo)
        return 1

    # Al terminar, enviar correo de fin
    enviar_correo_fin(lote)
    print('Proceso orquestado finalizado.')
    return 0
