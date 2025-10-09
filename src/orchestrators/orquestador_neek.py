import os
import json
import shutil
import getpass
from datetime import datetime
import subprocess
import sys

# Importar utilidades de rutas
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.path_utils import get_config_path, get_project_root, get_absolute_path

# We'll invoke the existing Electroneek/Python helper scripts as subprocesses when needed.


def read_variables(path_json=None):
    """
    Lee las variables globales desde el archivo de configuración.
    Optimizado para deployment en Azure donde el archivo siempre está en config/
    """
    usuario = getpass.getuser()
    
    # Si se pasa una ruta específica (útil para testing), usarla
    if path_json and os.path.isfile(path_json):
        config_path = path_json
        print(f"[DEBUG] Usando ruta personalizada: {config_path}")
    else:
        # En producción Azure, siempre usar la ubicación estándar
        config_path = get_config_path()
        print(f"[DEBUG] Usando ruta estándar: {config_path}")
    
    # Validar que el archivo existe
    if not os.path.isfile(config_path):
        raise FileNotFoundError(
            f'VariablesGlobales.json no encontrada en: {config_path}\n'
            f'Asegúrate de que el archivo existe en la carpeta config.\n'
            f'Usuario actual: {usuario}'
        )
    
    # Cargar y validar el archivo JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validar que tiene la estructura esperada
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("El archivo JSON debe contener al menos un objeto en un array")
        
        print(f"[SUCCESS] Configuración cargada desde: {config_path}")
        return data[0], config_path
        
    except json.JSONDecodeError as e:
        raise ValueError(f'Error al leer JSON desde {config_path}: {e}')
    except Exception as e:
        raise RuntimeError(f'Error inesperado al leer configuración: {e}')


def enviar_correo_inicio(rutajson):
    # reutiliza el script que ya existe: iniciocorreogmailelectronek.py
    # el script espera como argumento la ruta al json; lo llamamos como subproceso
    try:
        gateway_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../gateways/iniciocorreogmailelectronek.py'))
        subprocess.run([sys.executable, gateway_path, rutajson], check=True)
    except Exception as e:
        print('Warning: envío correo inicio falló', e)


def enviar_correo_fin(rutajson, lote):
    try:
        # fincorreogmailelectronek.py espera la ruta y el lote en el mismo formato que lo usa el proyecto.
        gateway_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../gateways/fincorreogmailelectronek.py'))
        subprocess.run([sys.executable, gateway_path, lote], check=True)
    except Exception as e:
        print('Warning: envío correo fin falló', e)


def enviar_correo_error(rutajson, cuerpo):
    # enviocorreogmailerrorelectronek.py recibe un argumento con formato: "ruta=cuerpo"
    try:
        param = f"{rutajson}={cuerpo}"
        gateway_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../gateways/enviocorreogmailerrorelectronek.py'))
        subprocess.run([sys.executable, gateway_path, param], check=True)
    except Exception as e:
        print('Warning: envío correo error falló', e)


def main(path_json=None):
    vars_obj, rutajson = read_variables(path_json)

    # Generar lote con fecha y hora compacta
    now = datetime.now()
    lote = now.strftime('%Y%m%d%H%M%S')

    # Preparar rutas y copia del excel si hace falta (convertir rutas relativas a absolutas)
    rutaradian = get_absolute_path(vars_obj.get('rutaradian')) if vars_obj.get('rutaradian') else None
    rutaradiancopia = get_absolute_path(vars_obj.get('rutaradiancopia')) if vars_obj.get('rutaradiancopia') else None
    rutaloop = get_absolute_path(vars_obj.get('rutaloop')) if vars_obj.get('rutaloop') else None

    # Si existe archivo original, hacer copia a la ruta copia usada por el resto del código
    if rutaradian and rutaradiancopia:
        try:
            shutil.copyfile(rutaradian, rutaradiancopia)
            print(f'Excel copiado a {rutaradiancopia}')
        except Exception as e:
            print('No se pudo copiar Excel, continuar si el archivo copia ya existe:', e)

    # Enviar correo de inicio (intento, no bloquear si falla)
    enviar_correo_inicio(rutajson)

    # Llamar al actual runner que recorre el excel; recorrerexcel.py acepta el path json como argumento
    try:
        # recorrerexcel.py expects the lote path as argument in the original flow; pass lote so logs include it
        service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/recorrerexcel.py'))
        subprocess.run([sys.executable, service_path, lote], check=True)
    except subprocess.CalledProcessError as e:
        # Si falló algo en el procesamiento, enviar correo de error con el mensaje
        cuerpo = f'Error al ejecutar recorrerexcel: returncode={e.returncode}'
        print(cuerpo)
        enviar_correo_error(rutajson, cuerpo)
        return 1

    # Al terminar, enviar correo de fin
    enviar_correo_fin(rutajson, lote)
    print('Proceso orquestado finalizado.')
    return 0


if __name__ == '__main__':
    # opcionalmente aceptar ruta a VariablesGlobales.json por argumento
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(main(arg))
