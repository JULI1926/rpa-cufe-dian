from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import os
import sys
import re
import json
import base64
from datetime import datetime

# Agregar la ruta del directorio padre para poder importar desde gateways
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from gateways.enpoint import post_facturas 
# Importar utilidades de rutas
from utils.path_utils import get_downloads_path, get_config_path, get_absolute_path 
import json
import pandas as pd
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import getpass
# Opción 1: Más simple y confiable
usuario = getpass.getuser()

# Obtener la fecha actual en formato YYYYMMDD
fecha_actual = datetime.now().strftime('%Y%m%d')

#RUTAS ARCHIVOS
descargas = get_downloads_path()
print("Ruta de Descargas:", descargas)

# Asegurarnos de que la carpeta de descargas exista (evita FileNotFoundError cuando se lista)
if not os.path.isdir(descargas):
    try:
        os.makedirs(descargas, exist_ok=True)
        print(f'Creada carpeta de descargas: {descargas}')
    except Exception as e:
        raise FileNotFoundError(f'No se pudo crear la carpeta de descargas {descargas}: {e}')

# Leer el archivo JSON usando ruta relativa
rutajson = get_config_path()
with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

# Asignar los valores a variables (convertir rutas relativas a absolutas)
ruta_carpeta = descargas
rutaimagen = get_absolute_path(primer_objeto['rutaimagen'])
rutaimagen2 = get_absolute_path(primer_objeto['rutaimagen2'])
rutaimagenpdf = get_absolute_path(primer_objeto['rutaimagenPDF'])
rutaimagenerror = get_absolute_path(primer_objeto['rutaimagenerror'])
nombrecliente = primer_objeto['nombrecliente']
documentocliente = primer_objeto['documentocliente']
rutatxt = get_absolute_path(primer_objeto['rutaloop'])
rutapdfbase64 = get_absolute_path(primer_objeto['rutapdfbase64'])
# Ruta donde se guardará el archivo JSON
ruta_json = get_absolute_path(primer_objeto['rutajsondatos'])
archivo_excel = get_absolute_path(primer_objeto['rutaradiancopia'])


def _search_and_click_templates(ruta1, ruta2=None, threshold=0.8, region=None):
    """Busca una o dos plantillas en una sola captura y hace click en el centro si encuentra alguna.
    Devuelve True si hizo click, False si no encontró ninguna.
    """
    try:
        tpl1 = cv2.imread(ruta1, cv2.IMREAD_GRAYSCALE) if ruta1 else None
    except Exception:
        tpl1 = None
    tpl2 = None
    if ruta2:
        try:
            tpl2 = cv2.imread(ruta2, cv2.IMREAD_GRAYSCALE)
        except Exception:
            tpl2 = None

    # Captura única (posible región para acelerar en el futuro)
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    for name, tpl in ((ruta1, tpl1), (ruta2, tpl2)):
        if tpl is None:
            continue
        try:
            res = cv2.matchTemplate(screenshot_gray, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
        except Exception:
            continue

        if max_val >= threshold:
            w, h = tpl.shape[1], tpl.shape[0]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            pyautogui.click(center_x, center_y)
            print(f"Click realizado con OpenCV usando plantilla: {os.path.basename(name) if name else 'tpl'} (score={max_val:.2f})")
            return True

    return False


# # dEFINIR vARIABLESgLOBALES
# ruta_carpeta = descargas
# rutaimagen= "DIAN/catchat.png"
# nombrecliente='Alejandro Bustos'
# documentocliente='1054990077'
# logeventos=f"DIAN/LogEventos{fecha_actual}.txt"
# logerrores=f"DIAN/LogErrores{fecha_actual}.txt"


#FUNCION NAVEGACION
def procesarfactura(cufeexcel,lote,logeventos,logerrores):

    ################################ELIMINAR ARCHIVOS PDF ########################################


    # Recorrer la carpeta y eliminar los archivos PDF
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):  # Verifica si es un archivo PDF
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            os.remove(ruta_archivo)  # Elimina el archivo
            #print(f"Eliminado: {archivo}")

    #print("Eliminación completada.")
    
    
    #NAVEGACION PARA CATCHAT
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-gpu')

    # driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # ✅ Así es como se usa con Selenium moderno
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    #Esta es la que funciona
    driver = webdriver.Chrome(options=options)
    # Maximizar la ventana
    #driver.maximize_window()


    driver.execute_script("window.open('https://catalogo-vpfe.dian.gov.co/User/SearchDocument', '_blank')")
    # Optimizado: reducir tiempo de espera de 15 a 5 segundos para abrir navegador
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    print("buscando pagina")
    cufe = cufeexcel
    

    ###########################ESCRBIR DATOS EN EL INPUT INGRESAR CUFE ##############################
    #contador=0
    for i in range(3):
        try:
            # Encontrar el input y escribir el valor ingresar el CUFE
            input_field = driver.find_element(By.XPATH, '//*[@id="DocumentKey"]')
            input_field.send_keys(cufe)
            break
        except Exception as e:
            print("ERROR NAVEGACION")
            driver.quit()
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorNavegacion | ERROR | No pudo Abrir Navegacion CUFE: {cufe} Intentos: {i}!\n"
            with open(logerrores, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
            if i == 3:
                return None
            else:
                # Optimizado: reducir tiempo de espera de 2 a 1 segundo para reintento de CUFE
                time.sleep(1)
                continue

    ########################################BUSCAR IMAGEN CATCHAT#####################################
    # Esperar a que cargue la página
    #time.sleep(3)
    #Clic Cordenadas
    # pyautogui.doubleClick(1093, 688)  #Doble clic en (500, 300)
    
    # try:
    #     # Buscar la imagen en la pantalla y hacer clic
    #     pos = pyautogui.locateCenterOnScreen(rutaimagen, confidence=0.6, grayscale=True)
    #     #pos = pyautogui.locateCenterOnScreen(rutaimagen, confidence=0.6, grayscale=True)

    #     # # Esperar a que cargue la página
    #     #time.sleep(4)
    #     if pos :
    #         #Clic Cordenadas
    #         #pyautogui.doubleClick(1093, 688)  #Doble clic en (500, 300)
    #         #Clic Imagen
    #         pyautogui.click(pos)
    #         print("Imagen encontrada y clickeada")
            
    #     else:
    #         print("Imagen no encontrada")
    #         # Cierra el navegador al final, pase lo que pase
    #         driver.quit()
    #         # Obtener la fecha y hora actual en el formato deseado
    #         fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    #         # Crear el mensaje de log
    #         mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Else: | Fin  Error CUFE: {cufe} !\n"

    #         # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
    #         with open(logerrores, "a", encoding="utf-8") as archivo:
    #             archivo.write(mensajeerror)
    #         return None
            
    # except Exception as e:
    #     # Cierra el navegador al final, pase lo que pase
    #         driver.quit()
    #         # Obtener la fecha y hora actual en el formato deseado
    #         fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    #         # Crear el mensaje de log
    #         mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Try: | Fin  Error CUFE: {cufe} !\n"

    #         # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
    #         with open(logerrores, "a", encoding="utf-8") as archivo:
    #             archivo.write(mensajeerror)
    #         return None

   

    ########################################BUSCAR IMAGEN CATCHAT#####################################
    # Esperar a que cargue la página
    time.sleep(3)

    # Intentar encontrar y clickear usando una sola captura para rutaimagen y opcional rutaimagen2
    if not _search_and_click_templates(rutaimagen, rutaimagen2, threshold=0.8):
        print("No se encontró la imagen con OpenCV.")
        # Cierra el navegador al final, pase lo que pase
        driver.quit()
        # Obtener la fecha y hora actual en el formato deseado
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        # Crear el mensaje de log
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Try: | Fin  Error CUFE: {cufe} !\n"

        # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

    
    ###########################BOTON BUSCAR CUFE DIAN###################################################
    #Esperar a que cargue la página
    time.sleep(3)
    try:
        search_button = driver.find_element(By.XPATH, '//*[@id="search-document-form"]/button')
        search_button.click()
    except Exception as e:
        # Cierra el navegador al final, pase lo que pase
            driver.quit()
            # Obtener la fecha y hora actual en el formato deseado
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            # Crear el mensaje de log
            mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Boton No encontrado Buscar Pagina Inicio DIAN: | Fin  Error CUFE: {cufe} !\n"

            # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
            with open(logerrores, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
            return None

    ###########################EXTRAER INPUT###################################################
    #Dar clic en Boton Buscar BOTON PDF
    time.sleep(4)
    # Obtener el texto del elemento usando XPath
    try:
        elemento = driver.find_element(By.XPATH, '//*[@id="search-document-form"]/div[2]/span')
        texto = elemento.text  # Obtener el contenido del <span>
        # Cargar el archivo Excel
        if "Documento no encontrado" in texto:
            #archivo_excel = "DIAN/RADIANCopia.xlsx"
            df = pd.read_excel(archivo_excel)
            #df.info()
            # Filtrar las filas donde la columna "CUFE" NO contenga los valores de dato1 y dato2
            df = df[~df["CUFE/CUDE"].isin([cufe])]

            # Guardar los cambios en el mismo archivo
            df.to_excel(archivo_excel, index=False)

            driver.quit()
            # Obtener la fecha y hora actual en el formato deseado
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            # Crear el mensaje de log
            mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Cufe No encontrado No existe Documento no encontrado en los registros de la DIAN.: | Fin  Error CUFE: {cufe} !\n"

            # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
            with open(logerrores, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
            return None
    except Exception as e:
        print()


    ########################################BUSCAR IMAGEN CATCHAT#####################################
    # Esperar a que cargue la página
    time.sleep(6)

    if _search_and_click_templates(rutaimagen, rutaimagen2, threshold=0.8):
        print("Click realizado con OpenCV.")
        # Esperar a que cargue la página
        time.sleep(5)
    else:
        print("No se encontró la imagen con OpenCV.")
        # Cierra el navegador al final, pase lo que pase
        driver.quit()
        # Obtener la fecha y hora actual en el formato deseado
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        # Crear el mensaje de log
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Try: | Fin  Error CUFE: {cufe} !\n"

        # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

   
    ########################### BOTON DESCARGAR PDF###################################################
     #Dar clic en Boton Buscar BOTON PDF
    time.sleep(2)
    
    try:
        #CLIC EN IMAGEN DESACRAGR PDF
        pos2 = pyautogui.locateCenterOnScreen(rutaimagenpdf, confidence=0.8)
        if pos2 :
            #Clic Coordenadas
            #pyautogui.doubleClick(2691, 449)  # Doble clic en (500, 300)

            #Click Imagen
            pyautogui.click(pos2)
            print("Imagen encontrada y clickeada Descargar PDF")
            time.sleep(2)
        
        
    except Exception as e:
        search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(//a[@class='downloadPDFUrl'])[1]"))
        )
        #search_button.click()
        # search_button = driver.find_element(By.XPATH, "(//a[@class='downloadPDFUrl'])[1]")
        # search_button.click()
        if search_button:  # Verifica si el elemento existe
            search_button.click()
            #print("✅ Botón encontrado y clickeado")
        
        try:
            search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[@id='html-gdoc']//a)[1]"))
            )
            search_button.click()
            
        except Exception as e:
            print()
            # Cierra el navegador al final, pase lo que pase
            driver.quit()
            # Obtener la fecha y hora actual en el formato deseado
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            # Crear el mensaje de log
            mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Boton No encontrado Descargar PDF Pagina DIAN: | Fin  Error CUFE: {cufe} !\n"

            # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
            with open(logerrores, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
            return None
        

    ########################################BUSCAR IMAGEN ERROR#####################################
    print("=== [DEBUG] INICIANDO BUSQUEDA DE IMAGEN ERROR ===")
    
    # Esperar a que cargue la página
    time.sleep(3)

    # Validar que la imagen de error existe
    if not os.path.exists(rutaimagenerror):
        print(f"[ERROR] No existe la imagen de error: {rutaimagenerror}")
        driver.quit()
        return None
    
    print(f"[DEBUG] Buscando imagen error en: {rutaimagenerror}")

    # Cargar imagen de plantilla
    template = cv2.imread(rutaimagenerror, cv2.IMREAD_COLOR)
    w, h = template.shape[1], template.shape[0]

    # Capturar pantalla
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Usar coincidencia de plantilla
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Umbral de coincidencia
    threshold = 0.8
    print(f"[DEBUG] Coincidencia imagen error: {max_val:.3f} (umbral: {threshold})")
    
    if max_val >= threshold:
        print("[DEBUG] Imagen error encontrada, haciendo click...")
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        pyautogui.click(center_x, center_y)
        print("Click realizado con OpenCV.")
        
        ########################################BUSCAR IMAGEN CATCHAT (SEGUNDO)#####################################
        print("=== [DEBUG] INICIANDO SEGUNDO CAPTCHA ===")
        
        # Esperar a que cargue la página
        time.sleep(8)
        print("[DEBUG] Esperando carga de pagina para segundo captcha...")

        # Cargar imagen de plantilla y buscar con la rutina optimizada (intenta rutaimagen y rutaimagen2)
        time.sleep(8)
        print(f"[DEBUG] Intentando segundo captcha con imagenes:")
        print(f"  - Imagen 1: {rutaimagen}")
        print(f"  - Imagen 2: {rutaimagen2}")
        
        if _search_and_click_templates(rutaimagen, rutaimagen2, threshold=0.8):
            print("=== [SUCCESS] SEGUNDO CAPTCHA COMPLETADO ===")
            print("Click realizado con OpenCV.")

            ########################### BOTON DESCARGAR PDF###################################################
            #Dar clic en Boton Buscar BOTON PDF
            time.sleep(4)
            
            try:
                #CLIC EN IMAGEN DESACRAGR PDF
                pos2 = pyautogui.locateCenterOnScreen(rutaimagenpdf, confidence=0.8)
                if pos2 :
                    #Clic Coordenadas
                    #pyautogui.doubleClick(2691, 449)  # Doble clic en (500, 300)

                    #Click Imagen
                    pyautogui.click(pos2)
                    print("Imagen encontrada y clickeada Descargar PDF")
                    time.sleep(2)
                
                
            except Exception as e:
                search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[@class='downloadPDFUrl'])[1]"))
                )
                #search_button.click()
                # search_button = driver.find_element(By.XPATH, "(//a[@class='downloadPDFUrl'])[1]")
                # search_button.click()
                if search_button:  # Verifica si el elemento existe
                    search_button.click()
                    #print("✅ Botón encontrado y clickeado")
                
                try:
                    search_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//div[@id='html-gdoc']//a)[1]"))
                    )
                    search_button.click()
                    
                except Exception as e:
                    print()
                    # Cierra el navegador al final, pase lo que pase
                    driver.quit()
                    # Obtener la fecha y hora actual en el formato deseado
                    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
                    # Crear el mensaje de log
                    mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Boton No encontrado Descargar PDF Pagina DIAN: | Fin  Error CUFE: {cufe} !\n"

                    # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
                    with open(logerrores, "a", encoding="utf-8") as archivo:
                        archivo.write(mensajeerror)
                    return None
        else:
            print("=== [ERROR] SEGUNDO CAPTCHA NO ENCONTRADO ===")
            print("No se encontró la imagen con OpenCV.")
            print("[DEBUG] El proceso continuara sin segundo captcha...")
    else:
        print("[DEBUG] No se encontro imagen de error, continuando sin segundo captcha...")
        print(f"[DEBUG] Coincidencia: {max_val:.3f} < {threshold}")
        

    # Esperar a que cargue la página
    time.sleep(2)

    #os.system(f"taskkill /f /im AcroRd32.exe")  # Cierra Adobe Reader (si se usa)
    #print("El PDF ha sido bloqueado para que no se abra automáticamente.")

    ################################EXTRAER VALORES ACUSE ########################################

    #CICLO PARA ENCONTRAR EL NUMERO DEL EVENTO
    suma=1
    contador = 0
    acuse=False
    reclamo=False
    recibo=False
    aceptacion=False
    while contador < 4:
        print("Suma:",suma)
        # Extraer el dato con XPath
        # Construir el XPath dinámicamente con f-string
        xpath = f"(//td[@class='text-center'])[{suma}]"
        elemento=''
        texto_elemento=''
        try:
            #elemento = driver.find_element(By.XPATH, "(//td[@class='text-center'])[1]")
            elemento = driver.find_element(By.XPATH, xpath)
            #print("Elemento encontrado: ",elemento.text)
            texto_elemento = elemento.text  # Guardar el texto en una variable
            texto_elemento=str(texto_elemento)
            print("Elemento encontrado: ",texto_elemento)

            # texto_elemento = texto_elemento.strip()
            #print("Elemento encontrado:-",texto_elemento,"-")
            if texto_elemento in "":
                print("Entro al if",texto_elemento)
            else:
                print("else ",texto_elemento)
                #ACUSE
                if '030' in texto_elemento:
                    acuse=True
            
                #RECLAMO
                if  '031' in texto_elemento:
                    reclamo=True
                    print("encontrado reclamo: ",texto_elemento)
            
                #RECIBIDO
                if '032' in texto_elemento:
                    recibo=True
                
                #ACEPTACION
                if '033' in texto_elemento:
                    aceptacion=True
                
        
        except Exception as e:
            print("No se encontró el dato.")
        suma=suma+4
        #print("Suma: ", suma)
        contador += 1  # Incrementa el contador
    print("Reclamo: ",reclamo)

    ################################FOLIOS########################################

    try:
        #EXTRAER DATOS FOLIO 1 DATOS DE LA FACTURA
        elemento1 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][1]")
        #print("Elemento encontrado1: ",elemento1.text)
        texto_elemento1 = elemento1.text  # Guardar el texto en una variable

        # Expresiones regulares para extraer datos
        patron_serie = r"Serie:\s*([\w\d]+)"
        patron_folio = r"Folio:\s*([\d]+)"
        patron_fecha = r"Fecha de emisión de la factura Electrónica:\s*([\d-]+)"

        # Buscar coincidencias en el texto
        match_serie = re.search(patron_serie, texto_elemento1)
        match_folio = re.search(patron_folio, texto_elemento1)
        match_fecha = re.search(patron_fecha, texto_elemento1)

        # Asignar valores a variables
        serie = match_serie.group(1) if match_serie else None
        folio = match_folio.group(1) if match_folio else None
        fecha_emision = match_fecha.group(1) if match_fecha else None

        # Mostrar resultados
        # print(f"Serie: {serie}")
        # print(f"Folio: {folio}")
        # print(f"Fecha de emisión: {fecha_emision}")

    except Exception as e:
            print("No se encontró el dato.")
            serie='Revisar Xpath'
            folio='Revisar Xpath'
            fecha = datetime.now().strftime("%d-%m-%Y")
            fecha_emision=str(fecha)
    
    if fecha_emision is None:
        print("La variable FECHA es None")
        # Expresión regular para capturar el número después de "N°. Identificación:"
        match = re.search(r"Fecha de emisión del documento soporte:\s*([\d-]+)", texto_elemento1)

        if match:
            fecha_emision = match.group(1)
            print("Fecha :", fecha_emision)
    
    if serie is None:
         print("La variable Serie es None")
         serie='Vacio'

            
    ################################ DATOS EMISOR ########################################

    try:

        #EXTRAER DATOS FOLIO 2 DATOS DEL EMISOR
        elemento2 = driver.find_element(By.XPATH, "//div[@class='row line-bottom row-fe-details'][2]/div[@class='col-md-4'][1]/p")
        #print("Elemento encontrado1: ",elemento2.text)
        texto_elemento2 = elemento2.text  # Guardar el texto en una variable


        # Expresión regular para extraer NIT y Nombre
        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        # Buscar coincidencias en el texto
        match_nit = re.search(patron_nit, texto_elemento2)
        match_nombre = re.search(patron_nombre, texto_elemento2)

        # Asignar valores a variables
        nit = match_nit.group(1) if match_nit else None
        nombre = match_nombre.group(1) if match_nombre else None

        # Mostrar resultados
        # print(f"NIT Emisor: {nit}")
        # print(f"Nombre Emisor: {nombre}")
    
    except Exception as e:
        #EXTRAER DATOS FOLIO 2 DATOS DEL EMISOR
        elemento2 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][1]/p")
        #print("Elemento encontrado1: ",elemento2.text)
        texto_elemento2 = elemento2.text  # Guardar el texto en una variable


        # Expresión regular para extraer NIT y Nombre
        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        # Buscar coincidencias en el texto
        match_nit = re.search(patron_nit, texto_elemento2)
        match_nombre = re.search(patron_nombre, texto_elemento2)

        # Asignar valores a variables
        nit = match_nit.group(1) if match_nit else None
        nombre = match_nombre.group(1) if match_nombre else None

        # Mostrar resultados
        # print(f"NIT Emisor: {nit}")
        # print(f"Nombre Emisor: {nombre}")
        # try:
        #     nit='Revisar Xpath'
        #     nombre='Revisar Xpath'
        # except Exception as e:
        #     print()

    ################################ DATOS RECEPTOR ########################################

    try:
        #EXTRAER DATOS FOLIO 3 DATOS DEL RECEPTOR
        elemento3 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][2]")
        #print("Elemento encontrado2: ",elemento3.text)
        texto_elemento3 = elemento3.text  # Guardar el texto en una variable

        # Expresiones regulares para extraer NIT y Nombre
        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        # Buscar coincidencias en el texto
        match_nit = re.search(patron_nit, texto_elemento3)
        match_nombre = re.search(patron_nombre, texto_elemento3)

        # Asignar valores a variables
        nit_receptor = match_nit.group(1) if match_nit else None
        nombre_receptor = match_nombre.group(1) if match_nombre else None

        # Mostrar resultados
        # print(f"NIT Receptor: {nit_receptor}")
        # print(f"Nombre Receptor: {nombre_receptor}")
    
    except Exception as e:
        #EXTRAER DATOS FOLIO 3 DATOS DEL RECEPTOR
        elemento3 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][2]/p")
        #print("Elemento encontrado2: ",elemento3.text)
        texto_elemento3 = elemento3.text  # Guardar el texto en una variable

        # Expresiones regulares para extraer NIT y Nombre
        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        # Buscar coincidencias en el texto
        match_nit = re.search(patron_nit, texto_elemento3)
        match_nombre = re.search(patron_nombre, texto_elemento3)

        # Asignar valores a variables
        nit_receptor = match_nit.group(1) if match_nit else None
        nombre_receptor = match_nombre.group(1) if match_nombre else None

        # Mostrar resultados
        # print(f"NIT Receptor: {nit_receptor}")
        # print(f"Nombre Receptor: {nombre_receptor}")
        # try:
        #     nit_receptor='Revisar Xpath'
        #     nombre_receptor='Revisar Xpath'
        # except Exception as e:
        #     print()

    if nit_receptor is None:
        print("La variable es None")
        # Expresión regular para capturar el número después de "N°. Identificación:"
        match = re.search(r"N°\. Identificación:\s*(\d+)", texto_elemento3)

        if match:
            nit_receptor = match.group(1)
            #print("Número de Identificación:", nit_receptor)

    if nit_receptor is None:
        #print("La variable es None NIT RECEPTOR")
        # Buscar el NIT con regex
        patron = r"NIT:\s*([A-Za-z0-9]+)"
        coincidencia = re.search(patron, texto_elemento3)

        if coincidencia:
            nit_receptor = coincidencia.group(1)  # Extrae el valor del NIT
            #print("NIT encontrado:", nit_receptor)
        else:
            print("NIT no encontrado")


    ################################ VALORES ########################################

    try:

        #EXTRAER DATOS FOLIO 4 DATOS DE LOS VALORES
        elemento4 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][3]")
        #print("Elemento encontrado3: ",elemento4.text)
        texto_elemento4 = elemento4.text  # Guardar el texto en una variable

        # Expresión regular para extraer los valores
        patron_iva = r"IVA:\s*\$([\d,]+)"
        patron_total = r"Total:\s*\$([\d,]+)"

        # Buscar los valores en el texto
        match_iva = re.search(patron_iva, texto_elemento4)
        match_total = re.search(patron_total, texto_elemento4)

        # Asignar valores a variables, eliminando comas
        iva = match_iva.group(1).replace(",", "") if match_iva else None
        total = match_total.group(1).replace(",", "") if match_total else None

        # Convertir a enteros si se encontraron los valores
        iva = int(iva) if iva else 0
        total = int(total) if total else 0

        # Mostrar resultados
        # print(f"IVA: {iva}")
        # print(f"Total: {total}")

    except Exception as e:
        #EXTRAER DATOS FOLIO 4 DATOS DE LOS VALORES
        elemento4 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][4]/p[2]")
        #print("Elemento encontrado3: ",elemento4.text)
        texto_elemento4 = elemento4.text  # Guardar el texto en una variable

        # Expresión regular para extraer los valores
        patron_iva = r"IVA:\s*\$([\d,]+)"
        patron_total = r"Total:\s*\$([\d,]+)"

        # Buscar los valores en el texto
        match_iva = re.search(patron_iva, texto_elemento4)
        match_total = re.search(patron_total, texto_elemento4)

        # Asignar valores a variables, eliminando comas
        iva = match_iva.group(1).replace(",", "") if match_iva else None
        total = match_total.group(1).replace(",", "") if match_total else None

        # Convertir a enteros si se encontraron los valores
        iva = int(iva) if iva else 0
        total = int(total) if total else 0

        # Mostrar resultados
        # print(f"IVA: {iva}")
        # print(f"Total: {total}")
        # try:
        #     iva=0
        #     total=0
        # except Exception as e:
        #     print()

    # # Mostrar resultados
    # print("DATOS FINALES")
    # print(f"Serie: {serie}")
    # print(f"Folio: {folio}")
    # print(f"Fecha de emisión: {fecha_emision}")
    # print(f"NIT Emisor: {nit}")
    # print(f"Nombre Emisor: {nombre}")
    # print(f"NIT Receptor: {nit_receptor}")
    # print(f"Nombre Receptor: {nombre_receptor}")
    # print(f"IVA: {iva}")
    # print(f"Total: {total}")
    ###########################PDF BASE 64 ######################################
    # Listar archivos en la carpeta y filtrar los PDF
    archivos_pdf = [archivo for archivo in os.listdir(descargas) if archivo.endswith(".pdf")]

    # Verificar si hay archivos PDF
    if archivos_pdf:
        for archivo in archivos_pdf:
            #print(f"Archivo encontrado: {archivo}")
            ruta_pdf2=descargas+"/"+archivo
            # Leer el archivo en modo binario y convertirlo a Base64
            with open(ruta_pdf2, "rb") as archivo:
                base64_pdf = base64.b64encode(archivo.read()).decode("utf-8")

            # Imprimir la cadena Base64 (puede ser muy larga)
            #print(base64_pdf)

            # Guardar la cadena Base64 en un archivo
            with open(rutapdfbase64, "w", encoding="utf-8") as archivo_salida:
                archivo_salida.write(base64_pdf)
        time.sleep(1)

    #         print("Conversión completada y guardada en documento_base64.txt")
    else:
        #print("No se encontraron archivos PDF en la carpeta Descargas.")
        base64_pdf='No se encontro PDF'


    ###########################CREAR JSON ######################################

    # if iva == 0:
    #     iva=1

    # Crear un diccionario con los datos
    datos = {
        "clienteNombre": nombrecliente,
        "clienteDocumento": documentocliente,
        "LOTE": lote,
        "CUFE": cufe,
        "nombreEmisor": nombre,
        "nitEmisor": nit,
        "nombreReceptor": nombre_receptor,
        "nitReceptor": nit_receptor,
        "fechaEmision": fecha_emision,
        "folio": folio,
        "serie": serie,
        "IVA": iva,
        "total": total,
        "PDF": base64_pdf,
        "eventos": {
            "Acuse030": acuse,
            "Reclamo031": reclamo,
            "Recibo032": recibo,
            "Aceptacion033": aceptacion
        }
        
    }

    # Crear un diccionario con los datos
    pdf='Pendiente'
    datos2 = {
        "clienteNombre": nombrecliente,
        "clienteDocumento": documentocliente,
        "LOTE": lote,
        "CUFE": cufe,
        "nombreEmisor": nombre,
        "nitEmisor": nit,
        "nombreReceptor": nombre_receptor,
        "nitReceptor": nit_receptor,
        "fechaEmision": fecha_emision,
        "folio": folio,
        "serie": serie,
        "IVA": iva,
        "total": total,
        "PDF": pdf,
        "eventos": {
            "Acuse030": acuse,
            "Reclamo031": reclamo,
            "Recibo032": recibo,
            "Aceptacion033": aceptacion
        }
        
    }

    
    # Guardar el diccionario como un archivo JSON
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    #print(f"Archivo JSON guardado en: {ruta_json}")

    #RESPUESTA EMPOINT
    response=post_facturas(datos)
    print("RESPONSE: ",response)
    # Si la llamada al endpoint falló y devolvió None, no seguir intentando indexar la respuesta
    if not response:
        print("No se obtuvo respuesta del endpoint /facturas. Ver logs para más detalles.")
        # Obtener la fecha y hora actual en el formato deseado
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        # Crear el mensaje de log
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | No se obtuvo respuesta del endpoint /facturas. Datos RPA: {datos2} | Fin  Error CUFE: {cufe}!\n"

        # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        # Indicar al llamador que la función falló para que se registre y continue con la siguiente fila
        return None

    # Si recibimos un objeto/dict respuesta, procesarlo como antes
    try:
        status_code = response.get("status") if isinstance(response, dict) else None
    except Exception:
        status_code = None

    if status_code != 200:
        print("ERROR en endpoint /facturas, status:", status_code)
        # Obtener la fecha y hora actual en el formato deseado
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        # Crear el mensaje de log
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Finalizo Registro Factura: {folio} | Fin  Error CUFE: {cufe} RespuestaEmpoint: {response} Datos RPA: {datos2}!\n"

        # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

    # Éxito
    print("OK")
    # Obtener la fecha y hora actual en el formato deseado
    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    # Crear el mensaje de log
    mensaje2 = f"FECHA: [{fecha_actual}] | INFO | DescargaRegistro | Finalizo Registro Factura: {folio} | Registro  con exito CUFE: {cufe}  RespuestaEmpoint: {response}!\n"

    # Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
    with open(logeventos, "a", encoding="utf-8") as archivo:
        archivo.write(mensaje2)


   
    ################################ELIMINAR ARCHIVOS PDF ########################################


    # Recorrer la carpeta y eliminar los archivos PDF
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):  # Verifica si es un archivo PDF
            time.sleep(1)
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            os.remove(ruta_archivo)  # Elimina el archivo
            #print(f"Eliminado: {archivo}")

    ################################ELIMINAR FILA ARCHIVOS EXCEL ########################################
    # Cargar el archivo Excel
    #archivo_excel = "DIAN/RADIANCopia.xlsx"
    df = pd.read_excel(archivo_excel)
    #df.info()
    # Filtrar las filas donde la columna "CUFE" NO contenga los valores de dato1 y dato2
    df = df[~df["CUFE/CUDE"].isin([cufe])]

    # Guardar los cambios en el mismo archivo
    df.to_excel(archivo_excel, index=False)


    # Cierra el navegador al final, pase lo que pase
    driver.quit()
    #print("Navegador cerrado")
    # Cierra los navegadores más usados
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM msedge.exe")
    os.system("taskkill /F /IM firefox.exe")
    os.system("taskkill /F /IM brave.exe")
    # Cierra todos los procesos de Google Chrome
    os.system("taskkill /f /im chrome.exe")

    print("Salida exitosa")
    # Indicar al llamador que la función terminó correctamente
    return True

