import pandas as pd
import sys
import os

# Agregar el directorio padre al path para importar navegaciondian
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from navegaciondian import procesarfactura 
import json
from datetime import datetime
import getpass

usuario = getpass.getuser()
print("Usuario del equipo:", usuario)

#TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON (opcional)
if len(sys.argv) > 1:
    lote = os.path.abspath(sys.argv[1])
    # Si el argumento viene como una ruta (por ejemplo inyectada por un runner), tomar solo el nombre final
    try:
        lote = os.path.basename(lote)
    except Exception:
        pass
else:
    # Permitir ejecutar el script directamente para pruebas: generar lote por timestamp
    from datetime import datetime as _dt
    lote = _dt.now().strftime('%Y%m%d%H%M%S')
    print(f'No se proporcionó argumento lote; usando lote por defecto: {lote}')

# #TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON
# parametros = os.path.abspath(sys.argv[1])

# #SEPARAMOS LA CADENA
# cadena=parametros.split('=')

# #SEPARAMOS LA CADENA POR POSICIONES
# #carpeta=cadena[0]
# rutajson=cadena[0]
# loop=cadena[1]

# Obtener la fecha actual en formato YYYYMMDD
fecha_actual = datetime.now().strftime('%Y%m%d')

# Leer el archivo JSON desde la nueva estructura
current_dir = os.path.dirname(os.path.abspath(__file__))
rutajson = os.path.abspath(os.path.join(current_dir, '../../config/VariablesGlobales.json'))

# Fallback a la ruta original si no existe en la nueva estructura
if not os.path.exists(rutajson):
    rutajson = r'C:/Users/julia/Desktop/VALIDACIONES_DIAN/DIAN/VariablesGlobales.json'

with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

# Asignar los valores a variables
archivo_excel = primer_objeto['rutaradian']
documento = primer_objeto['documentocliente']
rutatxt = primer_objeto['rutaloop']
archivo_excelcopia = primer_objeto['rutaradiancopia']



# # Leer el archivo Excel original
# archivo_original =archivo_excel
# df = pd.read_excel(archivo_original)

# # Guardar la copia con otro nombre
archivo_copia = archivo_excelcopia
# df.to_excel(archivo_copia, index=False)

# print(f"Copia creada: {archivo_copia}")



# Leer el archivo Excel
#archivo_excel = "DIAN/RADIAN.xlsx"

# Cargar el archivo en un DataFrame
#df = pd.read_excel(archivo_excel)
df = pd.read_excel(archivo_copia)

#HORA
# # Obtener la fecha y hora actual en el formato deseado
# timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
# #print(timestamp)

# #Armar LOTE
# lote=documento+timestamp
# print(f"LOTE: {lote}")

# RUTA LOGS: usar carpeta solicitada por el usuario
base_logs = r"C:\Users\julia\Documents\Archivos Excel DIAN"
os.makedirs(base_logs, exist_ok=True)
logeventos = os.path.join(base_logs, f"LogEventos-{documento}{lote}.txt")
logerrores = os.path.join(base_logs, f"LogErrores-{documento}{lote}.txt")

# # Obtener la fecha y hora actual en el formato deseado
# fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
# # Crear el mensaje de log
# mensaje = f"FECHA: [{fecha_actual}] | INFO | IniciarRegistro | Inicio tarea | Inicio  con exito!\n"
# # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
# with open(logeventos, "a", encoding="utf-8") as archivo:
#     archivo.write(mensaje)

# Recorrer las filas y extraer columnas específicas (asumiendo que 'Orden' y 'NIT' son los nombres de las columnas)
for index, fila in df.iterrows():
    cufe = str(fila['CUFE/CUDE'])
    nit = str(fila['NIT Emisor'])
    resultado = procesarfactura(cufe,lote,logeventos,logerrores)
    if not resultado:
        # Registrar en log de errores que la navegación falló para este CUFE
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Falló procesar CUFE: {cufe} | Lote: {lote}\n"
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        print(f"Fila {index + 1} -> Orden: {cufe} (ERROR: imagen no encontrada o navegación fallida)")
        # Asegurarse de cerrar chrome por si queda abierto
        os.system("taskkill /f /im chrome.exe")
        # Continuar con la siguiente fila
        continue
    print(f"Fila {index + 1} -> Orden: {cufe}, NIT: {nit}")
    # Cierra todos los procesos de Google Chrome (post éxito)
    os.system("taskkill /f /im chrome.exe")


# Obtener la fecha y hora actual en el formato deseado
fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
# Crear el mensaje de log
mensaje = f"FECHA: [{fecha_actual}] | INFO | Fin Procesar Excel | Finalizo tarea | Finalizo  con exito!\n"
# Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
with open(logeventos, "a", encoding="utf-8") as archivo:
    archivo.write(mensaje)
    
print("Salida archivo excel")