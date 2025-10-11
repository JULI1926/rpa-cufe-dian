

# RPA DIAN API - FastAPI

Automatización RPA para validaciones DIAN usando FastAPI y Python.

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

Configura `config/VariablesGlobales.json` y el archivo `.env` con tus credenciales:

```
WEBSERVICE_URL=https://tu-api-dian.com
WEBSERVICE_USER=usuario
WEBSERVICE_PASSWORD=contraseña
```

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
2. Consulta facturas pendientes desde el endpoint.
3. Procesa cada factura navegando la página DIAN y resolviendo CAPTCHAs.
4. Envía resultados al endpoint y notificaciones por correo.
5. Genera logs en `C:/Users/{usuario}/Documents/Archivos DIAN/`.

## Notas técnicas

- Requiere Python 3.8+, Google Chrome y permisos de escritura en carpetas de logs.
- La contraseña de correo en `VariablesGlobales.json` debería moverse a `.env` por seguridad.
- La documentación Swagger se actualiza automáticamente.

---
Para detalles técnicos y ejecución manual, consulta el orquestador en `src/orchestrators/orquestador_neek.py`.