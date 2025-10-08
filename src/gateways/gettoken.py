import requests
from dotenv import load_dotenv
import os

def getToken():
    load_dotenv()
    USER = os.getenv("WEBSERVICE_USER")
    PASSWORD = os.getenv("WEBSERVICE_PASSWORD")
    URL = os.getenv("WEBSERVICE_URL")

    # Fallback: si no está en env, intentar leer VariablesGlobales.json
    if not URL:
        try:
            import json
            path = os.path.join(os.path.dirname(__file__), 'VariablesGlobales.json')
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        URL = data[0].get('url') or data[0].get('WEBSERVICE_URL')
        except Exception:
            URL = None

    params = {
        "usuario": USER,
        "clave": PASSWORD
    }

    if not URL:
        print('ERROR: WEBSERVICE_URL no definido en variables de entorno ni en VariablesGlobales.json')
        return None

    target = URL.rstrip('/') + "/auth/token"
    print(f"DEBUG getToken -> POST {target} params usuario={'SET' if USER else 'None'} clave={'SET' if PASSWORD else 'None'}")
    try:
        response = requests.post(target, data=params, timeout=15)
    except Exception as e:
        print("DEBUG getToken -> request exception:", e)
        return None

    print("DEBUG getToken -> status:", response.status_code)
    # Intentar mostrar body de respuesta (por si da pistas)
    try:
        print("DEBUG getToken -> body:", response.text[:1000])
    except Exception:
        pass

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception:
            print("DEBUG getToken -> no JSON in response")
            return None

        # Algunos servicios devuelven la propiedad en varias keys: response, token, access_token
        token = data.get("response") or data.get("token") or data.get("access_token") or data.get("accessToken")
        if token:
            print("DEBUG getToken -> token obtenido")
            return token
        else:
            print("DEBUG getToken -> respuesta 200 pero no se encontró token en body")
            return None
    else:
        print(f"Error al obtener el token. Código de estado: {response.status_code}")
        return None

