import os
import json
import base64

# Usar rutas relativas directas
descargas = "./downloads"  # Ruta relativa a downloads
print("Ruta de Descargas:", descargas)

# Leer el archivo JSON usando ruta relativa
rutajson = "./config/VariablesGlobales.json"
with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto


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
        print("Base64 generado exitosamente, longitud:", len(base64_pdf))
        
        # Nota: Ya no se guarda en archivo, se procesa directamente en memoria