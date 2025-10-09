import pandas as pd
import json
import os
import sys

#TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON
rutajson = os.path.abspath(sys.argv[1])

# Leer el archivo JSON
#rutajson='C:/Users/azureadmin/Documents/DIAN/Python/DIAN/VariablesGlobales.json'
with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

# Asignar los valores a variables
archivo_excel = primer_objeto['rutaradian']

# Cargar el archivo Excel
#archivo_excel = "DIAN/RADIAN.xlsx"  # Reemplaza con la ruta real
df = pd.read_excel(archivo_excel)

# # Filtrar por un nombre específico en la columna 'Nombre' (ajusta el nombre de la columna si es diferente)
# nombre_filtrado = "Factura electrónica"  # Reemplaza con el nombre que buscas
# df_filtrado = df[df["Tipo de documento"] == nombre_filtrado]
df_filtrado = df[
    (df["Tipo de documento"] == "Factura electrónica") |
    (df["Tipo de documento"] == "Factura electrónica de exportación") 
]



# Guardar el resultado en un nuevo archivo (opcional)
df_filtrado.to_excel(archivo_excel, index=False)

# Mostrar el resultado
#print(df_filtrado)
