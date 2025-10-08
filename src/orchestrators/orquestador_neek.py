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
    usuario = getpass.getuser()
    # If a path was provided, prefer it (it may be a path inserted by Electroneek)
    candidates = []
    if path_json:
        candidates.append(path_json)

    # Try config folder using utilities
    config_path = get_config_path()
    candidates.append(config_path)

    # Try a VariablesGlobales.json next to this script (common during development)
    script_local = os.path.join(os.path.dirname(__file__), 'VariablesGlobales.json')
    candidates.append(script_local)

    # Also try the DIAN folder in the repo root
    project_root = get_project_root()
    repo_path = os.path.join(project_root, 'VariablesGlobales.json')
    candidates.append(repo_path)
    repo_candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), 'VariablesGlobales.json'))
    candidates.append(repo_candidate)

    # Find the first existing candidate
    found = None
    for p in candidates:
        if p and os.path.isfile(p):
            found = p
            break

    if not found:
        msg = (
            'VariablesGlobales.json no encontrada. Asegúrate de que existe y pasa su ruta como argumento:\n'
            'python orquestador_neek.py "C:/ruta/a/VariablesGlobales.json"\n'
            f'Busqué en: {candidates}\n'
        )
        raise FileNotFoundError(msg)

    with open(found, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[0], found


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
