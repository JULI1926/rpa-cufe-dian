import os
import glob

# Lista de rutas comunes donde puede estar chromedriver.exe
usuario = os.path.expanduser('~')
rutas_posibles = [
    os.path.join(usuario, 'ElectroNeek', 'Studio Pro', 'chromedriver', 'chromedriver.exe'),
    os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Programs', 'chromedriver.exe'),
    r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
    r"C:\Windows\System32\chromedriver.exe",
]

# Buscar chromedriver en PATH completo del sistema
for path in os.environ["PATH"].split(os.pathsep):
    posibles = glob.glob(os.path.join(path, "chromedriver.exe"))
    rutas_posibles.extend(posibles)

# Eliminar archivos encontrados
eliminados = []
for ruta in set(rutas_posibles):
    if os.path.isfile(ruta):
        try:
            os.remove(ruta)
            eliminados.append(ruta)
        except Exception as e:
            print(f"No se pudo eliminar {ruta}: {e}")

# Resultado
if eliminados:
    print("Se eliminaron los siguientes archivos conflictivos de chromedriver.exe:")
    for archivo in eliminados:
        print(" -", archivo)
else:
    print("No se encontraron chromedriver.exe conflictivos o ya fueron eliminados.")
