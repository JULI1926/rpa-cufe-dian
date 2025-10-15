

# RPA DIAN API - FastAPI

Automatización RPA para validaciones DIAN usando FastAPI y Python. Procesa facturas desde base de datos remota.

## Estructura y Uso

```
rpa-dian/
├── main.py                # Servidor FastAPI principal
├── run.py                 # Script para ejecutar el servidor
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno (API DIAN)
├── src/                   # Código fuente
│   ├── controllers/       # Controladores HTTP
│   ├── orchestrators/     # Orquestador principal
│   ├── services/          # Procesamiento y navegación
│   ├── gateways/          # APIs externas y correos
│   └── utils/             # Utilidades
├── config/                # Configuración y recursos
│   ├── VariablesGlobales.json
│   └── *.png (imágenes)
└── docs/                  # Documentación adicional
```

## Instalación rápida

```bash
cd rpa-dian
pip install -r requirements.txt
```

## Configuración

### 1. Variables de entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con las credenciales de la API DIAN:

```env
# Credenciales JWT para autenticación con API DIAN
WEBSERVICE_USER=dian_user-api
WEBSERVICE_PASSWORD=tu_password_aqui
WEBSERVICE_URL=https://api-dian-afaqhveqgwcggqaf.eastus-01.azurewebsites.net
```

**Nota:** El archivo `.env` está en `.gitignore` para proteger tus credenciales. Usa `.env.example` como plantilla.

### 2. Configuración general (VariablesGlobales.json)

Configura `config/VariablesGlobales.json` con los datos de correo y otras variables del sistema.

### 3. Prueba de conexión

Verifica que las credenciales funcionen correctamente:

```bash
python test_api_connection.py
```

Este script probará la autenticación JWT y la conexión con la API DIAN.

## Ejecución

Puedes ejecutar el orquestador desde la API o manualmente:

**API REST:**
- Levanta el servidor: `python run.py` o `uvicorn main:app --reload`
- Accede a la documentación interactiva: http://localhost:8000/docs
- Endpoint principal: `POST /api/v1/dian/procesar`

**Manual (PowerShell):**
```powershell
python .\src\orchestrators\orquestador_neek.py "C:/ruta/a/VariablesGlobales.json"
```

## Flujo simplificado

1. El orquestador inicia y envía correo de inicio.
2. Consulta facturas pendientes desde base de datos remota.
3. Procesa cada factura navegando la página DIAN y resolviendo CAPTCHAs.
4. Envía resultados al endpoint y notificaciones por correo.
5. Genera logs en `C:/Users/{usuario}/Documents/Archivos DIAN/`.

## Notas técnicas

- Requiere Python 3.8+, Google Chrome y permisos de escritura en carpetas de logs.
- La contraseña de correo en `VariablesGlobales.json` debería moverse a `.env` por seguridad.
- La documentación Swagger se actualiza automáticamente.

---
Para detalles técnicos y ejecución manual, consulta el orquestador en `src/orchestrators/orquestador_neek.py`.