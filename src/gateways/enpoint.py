import requests
from dotenv import load_dotenv
import os
from .gettoken import getToken
from datetime import datetime, timedelta


def post_facturas(datos):
    
    """
    Realiza una solicitud POST al endpoint /facturas con los datos proporcionados.
    """
    token = getToken()

    if token:
        load_dotenv()
        url_base = os.getenv("WEBSERVICE_URL")
        if not url_base:
            # Fallback to VariablesGlobales.json
            try:
                import json
                path = os.path.join(os.path.dirname(__file__), 'VariablesGlobales.json')
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            url_base = data[0].get('url') or data[0].get('WEBSERVICE_URL')
            except Exception:
                url_base = None

        if not url_base:
            print('ERROR: WEBSERVICE_URL no definido. No se puede hacer POST.')
            return None

        url = url_base + "/facturas"
        
        headers = {
            "Authorization": f"Bearer {token}",
        }
        try:
            fecha_str=datos["fechaEmision"]
            fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
            fecha=str(fecha)
        except Exception as e:
            fecha = datetime.now().strftime("%d-%m-%Y")
            fecha=str(fecha)

        body = {
            "clienteNombre": datos["clienteNombre"],
            "clienteDocumento": datos["clienteDocumento"],
            "Lote": datos["LOTE"],
            "CUFE": datos["CUFE"],
            "nombreEmisor": datos["nombreEmisor"],
            "nitEmisor": datos["nitEmisor"],
            "nombreReceptor": datos["nombreReceptor"],
            "nitReceptor": datos["nitReceptor"],
            "fechaEmision": fecha,
            "folio": datos["folio"],
            "serie": datos["serie"],
            "IVA": datos["IVA"],
            "total": datos["total"],
            "PDF": datos["PDF"],
            "acuses": {
                "030": datos["eventos"]["Acuse030"],
                "031": datos["eventos"]["Reclamo031"],
                "032": datos["eventos"]["Recibo032"],
                "033": datos["eventos"]["Aceptacion033"]
            }
        }
        #print(body)

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al realizar POST /facturas. Código de estado: {response.status_code}")
            return response.json()
    else:
        print("No se pudo obtener el token.")
        return None

def get_facturas_reporte(lote, tipo_respuesta):
    """
    Realiza una solicitud GET al endpoint /facturas/reporte con los parámetros proporcionados.
    """
    token = getToken()

    if token:
        load_dotenv()
        url_base = os.getenv("WEBSERVICE_URL")
        if not url_base:
            try:
                import json
                path = os.path.join(os.path.dirname(__file__), 'VariablesGlobales.json')
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            url_base = data[0].get('url') or data[0].get('WEBSERVICE_URL')
            except Exception:
                url_base = None

        if not url_base:
            print('ERROR: WEBSERVICE_URL no definido. No se puede hacer GET reportes.')
            return None

        url = url_base + "/facturas/reporte"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        params = {
            "lote": lote,
            "tipoRespuesta": tipo_respuesta
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al realizar GET /facturas/reporte. Código de estado: {response.status_code}")
            return None
    else:
        print("No se pudo obtener el token.")
        return None

