import os
import json
import base64

# Importar utilidades de rutas
from path_utils import get_downloads_path, get_config_path, get_absolute_path

#RUTAS ARCHIVOS usando utilidades
descargas = get_downloads_path()
print("Ruta de Descargas:", descargas)

# Leer el archivo JSON usando utilidades de rutas
rutajson = get_config_path()
with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

rutapdfbase64 = get_absolute_path(primer_objeto['rutapdfbase64'])


###########################PDF BASE 64 ######################################
# Listar archivos en la carpeta y filtrar los PDF
archivos_pdf = [archivo for archivo in os.listdir(descargas) if archivo.endswith(".pdf")]

# Verificar si hay archivos PDF
if archivos_pdf:
    for archivo in archivos_pdf:
        print(f"Archivo encontrado: {archivo}")
        ruta_pdf2=descargas+"/"+archivo
        # Leer el archivo en modo binario y convertirlo a Base64
        with open(ruta_pdf2, "rb") as archivo:
            base64_pdf = base64.b64encode(archivo.read()).decode("utf-8")

        # Imprimir la cadena Base64 (puede ser muy larga)
        #print(base64_pdf)

        # Guardar la cadena Base64 en un archivo
        with open(rutapdfbase64, "w", encoding="utf-8") as archivo_salida:
            archivo_salida.write(base64_pdf)