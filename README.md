# RPA DIAN API - FastAPI

API REST para automatización RPA de validaciones DIAN con estructura FAZT API completamente en Python.

## 📋 Descripción

Este proyecto migra el RPA DIAN existente a una estructura FAZT API organizada usando FastAPI, manteniendo toda la funcionalidad original sin modificaciones en la lógica de negocio.

### Funcionalidades principales:

- ✅ **Procesamiento DIAN**: Ejecuta el orquestador principal que procesa facturas DIAN
- ✅ **Validación CUFE/CUDE**: Navega automáticamente por la página de DIAN usando Selenium
- ✅ **Notificaciones**: Envía correos de inicio, fin y errores 
- ✅ **Logs detallados**: Genera logs de eventos y errores
- ✅ **Documentación automática**: Swagger UI integrado

## 🏗️ Estructura del Proyecto

```
rpa-dian/
├── main.py                    # Servidor FastAPI principal
├── run.py                     # Script para ejecutar el servidor
├── requirements.txt           # Dependencias Python
├── README.md                 # Documentación
├── src/                      # Código fuente
│   ├── controllers/          # Controladores HTTP
│   │   └── dian_controller.py
│   ├── orchestrators/        # Lógica de orquestación
│   │   └── orquestador_neek.py
│   ├── services/            # Servicios de procesamiento
│   │   ├── navegaciondian.py
│   │   └── recorrerexcel.py
│   ├── gateways/            # APIs externas y correos
│   │   ├── gettoken.py
│   │   ├── iniciocorreogmailelectronek.py
│   │   ├── fincorreogmailelectronek.py
│   │   └── enviocorreogmailerrorelectronek.py
│   └── utils/               # Utilidades
│       ├── 3intentos.py
│       ├── abrirpagina.py
│       ├── cerrarpagina.py
│       └── ...
├── config/                  # Configuración
│   ├── VariablesGlobales.json
│   ├── datos_factura.json
│   ├── *.png (imágenes)
│   └── *.xlsx (archivos Excel)
├── docs/                   # Documentación
└── tests/                  # Tests (futuro)
```

## 🚀 Instalación y Uso

### 1. Instalar dependencias

```bash
cd rpa-dian
pip install -r requirements.txt
```

### 2. Configurar variables

Editar `config/VariablesGlobales.json` con las rutas y credenciales correctas.

### 3. Ejecutar servidor

```bash
# Opción 1: Usar el script run.py
python run.py

# Opción 2: Ejecutar directamente con uvicorn  
python main.py

# Opción 3: Usar uvicorn comando
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acceder a la API

- **Documentación Swagger**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 Endpoints de la API

### `POST /api/v1/dian/procesar`

Ejecuta el orquestador DIAN completo:

```json
{
  "path_json": "C:/ruta/personalizada/VariablesGlobales.json"  // Opcional
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Procesamiento DIAN completado exitosamente",
  "exit_code": 0,
  "output": "...",
  "timestamp": "2024-10-08T10:30:00"
}
```

### `GET /health`

Health check del servicio:

```json
{
  "success": true,
  "timestamp": "2024-10-08T10:30:00"
}
```

## 🔧 Configuración

El archivo `config/VariablesGlobales.json` contiene toda la configuración:

- **Rutas de archivos**: Excel, imágenes, PDFs, logs
- **Credenciales de correo**: Para notificaciones automáticas
- **URL DIAN**: Página de validación de facturas
- **Datos del cliente**: NIT y nombre

## 🐍 Migración Realizada

El proyecto original en `DIAN/` fue migrado manteniendo:

- ✅ **Funcionalidad intacta**: Toda la lógica RPA funciona igual
- ✅ **Estructura organizada**: Separación clara de responsabilidades  
- ✅ **API REST**: Endpoints HTTP para invocar el RPA
- ✅ **Documentación**: Swagger automático
- ✅ **Logs preservados**: Misma generación de logs
- ✅ **Configuración**: Mismo archivo JSON de configuración

## 🔍 Monitoreo

Los logs se generan en:
- `C:\Users\julia\Documents\Archivos Excel DIAN\LogEventos-{documento}{lote}.txt`
- `C:\Users\julia\Documents\Archivos Excel DIAN\LogErrores-{documento}{lote}.txt`

## 📧 Notificaciones

El sistema envía correos automáticamente:
- **Inicio**: Al comenzar el procesamiento
- **Fin**: Al completar exitosamente  
- **Error**: Si ocurre algún fallo

## 🛠️ Desarrollo

Para agregar nuevas funcionalidades:

1. **Controladores**: Agregar en `src/controllers/`
2. **Servicios**: Lógica de negocio en `src/services/`
3. **Gateways**: APIs externas en `src/gateways/`
4. **Utilidades**: Helpers en `src/utils/`

La documentación Swagger se actualiza automáticamente con los docstrings y anotaciones de tipo.

## 🚨 Consideraciones

- **Python**: Requiere Python 3.8+
- **Chrome**: Selenium necesita Google Chrome instalado
- **Permisos**: Requiere permisos de escritura en las carpetas de logs
- **Red**: Acceso a Internet para la página de DIAN y envío de correos