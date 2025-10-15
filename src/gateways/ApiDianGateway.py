"""
Gateway unificado para la API de DIAN
Centraliza todas las operaciones relacionadas con el webservice de DIAN
"""

import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime


class ApiDianGateway:
    """Gateway unificado para operaciones con la API de DIAN"""

    def __init__(self):
        """Inicializa el gateway con configuración base"""
        load_dotenv()
        self.base_url = self._get_base_url()
        self.user = os.getenv("WEBSERVICE_USER")
        self.password = os.getenv("WEBSERVICE_PASSWORD")
        
    def _get_base_url(self):
        """Obtiene la URL base del webservice desde variables de entorno"""
        return os.getenv("WEBSERVICE_URL")

    def get_token(self):
        """
        Obtiene token de autenticación del webservice
        
        Returns:
            str: Token de autorización o None en caso de error
        """
        if not self.base_url:
            print('ERROR: WEBSERVICE_URL no definido en variables de entorno (.env)')
            return None
            
        if not self.user or not self.password:
            print('ERROR: WEBSERVICE_USER o WEBSERVICE_PASSWORD no definidos en variables de entorno (.env)')
            return None

        params = {
            "usuario": self.user,
            "clave": self.password
        }

        target = self.base_url.rstrip('/') + "/auth/token"
        
        try:
            response = requests.post(target, data=params, timeout=15)
        except Exception as e:
            print("Error al obtener token:", e)
            return None

        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print("Error: Respuesta no es JSON válido")
                return None

            # Algunos servicios devuelven la propiedad en varias keys: response, token, access_token
            token = data.get("response") or data.get("token") or data.get("access_token") or data.get("accessToken")
            if token:
                return token
            else:
                print("Error: No se encontró token en la respuesta")
                return None
        else:
            print(f"Error al obtener el token. Código de estado: {response.status_code}")
            return None

    def _get_headers(self):
        """Obtiene headers con token de autorización"""
        token = self.get_token()
        if not token:
            raise Exception("No se pudo obtener el token de autorización")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def post_facturas(self, datos):
        """
        Realiza una solicitud POST al endpoint /facturas con los datos proporcionados.
        
        Args:
            datos (dict): Diccionario con los datos de la factura
            
        Returns:
            dict: Respuesta del servidor o None en caso de error
        """
        if not self.base_url:
            print('ERROR: WEBSERVICE_URL no definido en variables de entorno (.env)')
            return None

        url = f"{self.base_url}/facturas"
        
        try:
            headers = self._get_headers()
        except Exception as e:
            print(f"Error obteniendo token: {e}")
            return None

        # Procesar fecha de emisión
        try:
            fecha_str = datos["fechaEmision"]
            fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
            fecha = str(fecha)
        except Exception:
            fecha = datetime.now().strftime("%d-%m-%Y")
            fecha = str(fecha)

        # Preparar body de la petición
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

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al realizar POST /facturas. Código de estado: {response.status_code}")
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en POST /facturas: {e}")
            return None

    def get_facturas_reporte(self, lote, tipo_respuesta):
        """
        Realiza una solicitud GET al endpoint /facturas/reporte con los parámetros proporcionados.
        
        Args:
            lote (str): Identificador del lote
            tipo_respuesta (str): Tipo de respuesta solicitada
            
        Returns:
            dict: Respuesta del servidor o None en caso de error
        """
        if not self.base_url:
            print('ERROR: WEBSERVICE_URL no definido en variables de entorno (.env)')
            return None

        url = f"{self.base_url}/facturas/reporte"

        try:
            headers = self._get_headers()
        except Exception as e:
            print(f"Error obteniendo token: {e}")
            return None

        params = {
            "lote": lote,
            "tipoRespuesta": tipo_respuesta
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al realizar GET /facturas/reporte. Código de estado: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en GET /facturas/reporte: {e}")
            return None

    def get_facturas_faltantes(self):
        """
        Realiza una solicitud GET al endpoint /facturas/faltantes con JWT Bearer token.
        
        Returns:
            dict: Respuesta del servidor con las facturas faltantes o None en caso de error
        """
        if not self.base_url:
            print('ERROR: WEBSERVICE_URL no definido en variables de entorno (.env)')
            return None

        url = f"{self.base_url}/facturas/faltantes"

        try:
            headers = self._get_headers()
        except Exception as e:
            print(f"Error obteniendo token: {e}")
            return None

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al realizar GET /facturas/faltantes. Código de estado: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en GET /facturas/faltantes: {e}")
            return None


# Instancia global para compatibilidad con código existente
api_gateway = ApiDianGateway()

# Funciones wrapper para mantener compatibilidad
def post_facturas(datos):
    """Wrapper para mantener compatibilidad con código existente"""
    return api_gateway.post_facturas(datos)

def get_facturas_reporte(lote, tipo_respuesta):
    """Wrapper para mantener compatibilidad con código existente"""
    return api_gateway.get_facturas_reporte(lote, tipo_respuesta)

def get_facturas_faltantes():
    """Wrapper para obtener facturas faltantes"""
    return api_gateway.get_facturas_faltantes()