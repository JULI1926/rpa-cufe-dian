from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from gateways.ApiDianGateway import post_facturas
import time
import pyautogui
import os
import sys
import re
import json
import base64
import cv2
import numpy as np
import getpass
from datetime import datetime


# Variables globales que se inicializarán cuando sea necesario
usuario = None
fecha_actual = None
ruta_descargas_real = None

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

def init_config():
    """Inicializar configuración del módulo"""
    global usuario, fecha_actual, ruta_descargas_real
    
    usuario = getpass.getuser()
    fecha_actual = datetime.now().strftime('%Y%m%d')

    ruta_descargas_real = "I:\\"
    if not os.path.isdir(ruta_descargas_real):
        try:
            os.makedirs(ruta_descargas_real, exist_ok=True)
        except Exception:
            pass
    
    return ruta_descargas_real

def load_config():
    """Cargar configuración desde JSON"""
    rutajson = "./config/VariablesGlobales.json"
    with open(rutajson, 'r') as archivo:
        datos = json.load(archivo)

    primer_objeto = datos[0]
    
    if ruta_descargas_real is None:
        init_config()

    config = {
        'ruta_carpeta': ruta_descargas_real,  # Usar la ruta real donde se descargan los PDFs
        'rutaimagen': os.path.join("./config", primer_objeto['rutaimagen']),
        'rutaimagen2': os.path.join("./config", primer_objeto['rutaimagen2']),
        'rutaimagenpdf': os.path.join("./config", primer_objeto['rutaimagenPDF']),
        'rutaimagenerror': os.path.join("./config", primer_objeto['rutaimagenerror'])
        
    }
    
    return config

# Variables globales que se inicializarán cuando sea necesario
usuario = None
fecha_actual = None
ruta_descargas_real = None


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


def procesarfactura(cufeexcel, lote, logeventos, logerrores, client_name=None, client_document=None):
    # Cargar configuración al inicio
    config = load_config()
    ruta_carpeta = config['ruta_carpeta']
    rutaimagen = config['rutaimagen']
    rutaimagen2 = config['rutaimagen2']
    rutaimagenpdf = config['rutaimagenpdf']
    rutaimagenerror = config['rutaimagenerror']

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
    
    # Cargar también primer_objeto para usar en el resto de la función
    rutajson = "./config/VariablesGlobales.json"
    with open(rutajson, 'r') as archivo:
        datos = json.load(archivo)
    primer_objeto = datos[0]
    
    if client_name and client_document:
        nombre_cliente_actual = client_name
        documento_cliente_actual = client_document
    else:
        nombre_cliente_actual = primer_objeto.get('nombrecliente', 'Cliente por defecto')
        documento_cliente_actual = primer_objeto.get('documentocliente', '000000000')

    # Limpiar PDFs previos en la carpeta I:\
    try:
        for archivo in os.listdir(ruta_carpeta):
            if archivo.endswith(".pdf"):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                os.remove(ruta_archivo)
    except Exception:
        pass
    
    
    
    # Configuración específica para descarga de PDFs
    # Configuración de descarga de PDFs

    download_prefs = {
        "download.default_directory": ruta_carpeta,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,  # Forzar descarga en lugar de abrir en navegador
        "plugins.plugins_disabled": ["Chrome PDF Viewer"]  # Deshabilitar visor de PDF integrado
    }
    options.add_experimental_option("prefs", download_prefs)
    
    # Asegurar que la carpeta existe
    os.makedirs(ruta_carpeta, exist_ok=True)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_script("window.open('https://catalogo-vpfe.dian.gov.co/User/SearchDocument', '_blank')")
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    # ...existing code...
    cufe = cufeexcel
    
    for i in range(3):
        try:
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
                time.sleep(1)
                continue

    

    ########################################BUSCAR IMAGEN CAPTCHA#####################################
    # Esperar a que cargue la página
    time.sleep(3)

    # Loop de reintentos para captcha con refresh de página
    max_retries = 5
    captcha_resuelto = False
    
    for attempt in range(max_retries):
        print(f"[DEBUG] Intento {attempt + 1}/{max_retries} para resolver captcha")
        
        # Intentar encontrar y clickear usando una sola captura para rutaimagen y opcional rutaimagen2
        if _search_and_click_templates(rutaimagen, rutaimagen2, threshold=0.8):
            print(f"[DEBUG] Captcha resuelto exitosamente en intento {attempt + 1}")
            captcha_resuelto = True
            break
        else:
            print(f"[DEBUG] Captcha falló en intento {attempt + 1}")
            
            if attempt < max_retries - 1:  # No es el último intento
                print("[DEBUG] Refrescando página y reingresando CUFE...")
                
                # Refrescar la página
                driver.refresh()
                time.sleep(3)
                
                # Reingresar el CUFE
                try:
                    input_field = driver.find_element(By.XPATH, '//*[@id="DocumentKey"]')
                    input_field.clear()  # Limpiar campo antes de ingresar
                    input_field.send_keys(cufe)
                    time.sleep(2)
                except Exception as e:
                    print(f"[ERROR] Error reingresando CUFE en intento {attempt + 1}: {e}")
                    continue
            else:
                print("[ERROR] Máximo de reintentos alcanzado para captcha")
    
    if not captcha_resuelto:
        print("No se pudo resolver el captcha después de todos los reintentos.")
        # Cierra el navegador al final, pase lo que pase
        driver.quit()
        # Obtener la fecha y hora actual en el formato deseado
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        # Crear el mensaje de log
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Captcha No resuelto después de {max_retries} intentos | Fin Error CUFE: {cufe} !\n"

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
        driver.quit()
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Boton No encontrado Buscar Pagina Inicio DIAN: | Fin  Error CUFE: {cufe} !\n"

        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

    ###########################EXTRAER INPUT###################################################
    time.sleep(4)
    try:
        elemento = driver.find_element(By.XPATH, '//*[@id="search-document-form"]/div[2]/span')
        texto = elemento.text
        if "Documento no encontrado" in texto:
            driver.quit()
            fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
            mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Cufe No encontrado - No existe en los registros de la DIAN: | Fin Error CUFE: {cufe} !\n"

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
        time.sleep(5)
    else:
        print("No se encontró la imagen con OpenCV.")
        driver.quit()
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Try: | Fin  Error CUFE: {cufe} !\n"

        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

   
    ########################### DESCARGAR PDF ###################################################
    time.sleep(2)
    
    try:
        #CLIC EN IMAGEN DESCARGAR PDF
        pos2 = pyautogui.locateCenterOnScreen(rutaimagenpdf, confidence=0.8)
        if pos2 :
            pyautogui.click(pos2)
            print("Imagen encontrada y clickeada Descargar PDF")
            print("[DEBUG] Esperando descarga del PDF...")
            time.sleep(5)
        
        
    except Exception as e:
        search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(//a[@class='downloadPDFUrl'])[1]"))
        )
        if search_button:
            search_button.click()
            print("[DEBUG] Botón de descarga clickeado via XPath, esperando descarga...")
            time.sleep(5)
        
        try:
            search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[@id='html-gdoc']//a)[1]"))
            )
            search_button.click()
            print("[DEBUG] Segundo botón de descarga clickeado, esperando descarga...")
            time.sleep(5)
            
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
    
    time.sleep(3)

    if not os.path.exists(rutaimagenerror):
        print(f"[ERROR] No existe la imagen de error: {rutaimagenerror}")
        driver.quit()
        return None
    
    print(f"[DEBUG] Buscando imagen error en: {rutaimagenerror}")

    template = cv2.imread(rutaimagenerror, cv2.IMREAD_COLOR)
    w, h = template.shape[1], template.shape[0]

    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    threshold = 0.8
    print(f"[DEBUG] Coincidencia imagen error: {max_val:.3f} (umbral: {threshold})")
    
    if max_val >= threshold:
        print("[DEBUG] Imagen error encontrada, haciendo click...")
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        pyautogui.click(center_x, center_y)
        print("Click realizado con OpenCV.")

        ########################################SEGUNDO CAPTCHA#####################################
        print("=== [DEBUG] INICIANDO SEGUNDO CAPTCHA ===")

        time.sleep(0.3)  # Optimizado de 0.5 a 0.3 segundos
        print("[DEBUG] Esperando carga de pagina para segundo captcha...")

        time.sleep(0.3)  # Optimizado de 0.5 a 0.3 segundos
        print(f"[DEBUG] Intentando segundo captcha con imagenes:")
        print(f"  - Imagen 1: {rutaimagen}")
        print(f"  - Imagen 2: {rutaimagen2}")

        if _search_and_click_templates(rutaimagen, rutaimagen2, threshold=0.8):
            print("=== [SUCCESS] SEGUNDO CAPTCHA COMPLETADO ===")
            print("Click realizado con OpenCV.")

            ########################### DESCARGAR PDF (segundo captcha) ###################################################
            time.sleep(0.3)  # Optimizado de 0.5 a 0.3 segundos

            try:
                pos2 = pyautogui.locateCenterOnScreen(rutaimagenpdf, confidence=0.8)
                if pos2 :
                    pyautogui.click(pos2)
                    print("Imagen encontrada y clickeada Descargar PDF (segundo captcha)")
                    print("[DEBUG] Esperando descarga del PDF después del segundo captcha...")
                    time.sleep(0.3)  # Optimizado de 0.5 a 0.3 segundos
            except Exception as e:
                search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[@class='downloadPDFUrl'])[1]"))
                )
                if search_button:
                    search_button.click()
                    print("[DEBUG] Botón de descarga clickeado via XPath (segundo captcha), esperando descarga...")
                    time.sleep(5)
                
                try:
                    search_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//div[@id='html-gdoc']//a)[1]"))
                    )
                    search_button.click()
                    print("[DEBUG] Segundo botón de descarga clickeado (segundo captcha), esperando descarga...")
                    time.sleep(5)
                    
                except Exception as e:
                    print()
                    driver.quit()
                    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
                    mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Boton No encontrado Descargar PDF Pagina DIAN: | Fin  Error CUFE: {cufe} !\n"

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
        

    time.sleep(2)

    ################################EXTRAER EVENTOS DE ACUSE ########################################

    suma=1
    contador = 0
    acuse=False
    reclamo=False
    recibo=False
    aceptacion=False

    while contador < 4:
        print("Suma:",suma)
        xpath = f"(//td[@class='text-center'])[{suma}]"
        elemento=''
        texto_elemento=''
        try:
            elemento = driver.find_element(By.XPATH, xpath)
            texto_elemento = elemento.text
            texto_elemento=str(texto_elemento)
            print("Elemento encontrado: ",texto_elemento)

            if texto_elemento in "":
                print("Entro al if",texto_elemento)
            else:
                print("else ",texto_elemento)
                if '030' in texto_elemento:
                    acuse=True
        
                if  '031' in texto_elemento:
                    reclamo=True
                    print("encontrado reclamo: ",texto_elemento)
        
                if '032' in texto_elemento:
                    recibo=True
            
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
        elemento1 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][1]")
        texto_elemento1 = elemento1.text

        patron_serie = r"Serie:\s*([\w\d]+)"
        patron_folio = r"Folio:\s*([\d]+)"
        patron_fecha = r"Fecha de emisión de la factura Electrónica:\s*([\d-]+)"

        match_serie = re.search(patron_serie, texto_elemento1)
        match_folio = re.search(patron_folio, texto_elemento1)
        match_fecha = re.search(patron_fecha, texto_elemento1)

        serie = match_serie.group(1) if match_serie else None
        folio = match_folio.group(1) if match_folio else None
        fecha_emision = match_fecha.group(1) if match_fecha else None       

    except Exception as e:
            print("No se encontró el dato.")
            serie='Revisar Xpath'
            folio='Revisar Xpath'
            fecha = datetime.now().strftime("%d-%m-%Y")
            fecha_emision=str(fecha)
    
    if fecha_emision is None:
        print("La variable FECHA es None")
        match = re.search(r"Fecha de emisión del documento soporte:\s*([\d-]+)", texto_elemento1)

        if match:
            fecha_emision = match.group(1)
            print("Fecha :", fecha_emision)
    
    if serie is None:
         print("La variable Serie es None")
         serie='Vacio'

            
    ################################ DATOS EMISOR ########################################

    try:
        elemento2 = driver.find_element(By.XPATH, "//div[@class='row line-bottom row-fe-details'][2]/div[@class='col-md-4'][1]/p")
        texto_elemento2 = elemento2.text

        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        match_nit = re.search(patron_nit, texto_elemento2)
        match_nombre = re.search(patron_nombre, texto_elemento2)

        nit = match_nit.group(1) if match_nit else None
        nombre = match_nombre.group(1) if match_nombre else None
    
    except Exception as e:
        elemento2 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][1]/p")
        texto_elemento2 = elemento2.text

        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        match_nit = re.search(patron_nit, texto_elemento2)
        match_nombre = re.search(patron_nombre, texto_elemento2)

        nit = match_nit.group(1) if match_nit else None
        nombre = match_nombre.group(1) if match_nombre else None

    ################################ DATOS RECEPTOR ########################################

    try:
        elemento3 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][2]")
        texto_elemento3 = elemento3.text

        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        match_nit = re.search(patron_nit, texto_elemento3)
        match_nombre = re.search(patron_nombre, texto_elemento3)

        nit_receptor = match_nit.group(1) if match_nit else None
        nombre_receptor = match_nombre.group(1) if match_nombre else None
    
    except Exception as e:
        elemento3 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][2]/p")
        texto_elemento3 = elemento3.text

        patron_nit = r"NIT:\s*([\d]+)"
        patron_nombre = r"Nombre:\s*(.+)"

        match_nit = re.search(patron_nit, texto_elemento3)
        match_nombre = re.search(patron_nombre, texto_elemento3)

        nit_receptor = match_nit.group(1) if match_nit else None
        nombre_receptor = match_nombre.group(1) if match_nombre else None

        

    if nit_receptor is None:
        print("La variable es None")
        match = re.search(r"N°\. Identificación:\s*(\d+)", texto_elemento3)

        if match:
            nit_receptor = match.group(1)

    if nit_receptor is None:
        patron = r"NIT:\s*([A-Za-z0-9]+)"
        coincidencia = re.search(patron, texto_elemento3)

        if coincidencia:
            nit_receptor = coincidencia.group(1)
        else:
            print("NIT no encontrado")


    ################################ VALORES ########################################

    try:
        elemento4 = driver.find_element(By.XPATH, "//div[@class='col-md-4'][3]")
        texto_elemento4 = elemento4.text

        patron_iva = r"IVA:\s*\$([\d,]+)"
        patron_total = r"Total:\s*\$([\d,]+)"

        match_iva = re.search(patron_iva, texto_elemento4)
        match_total = re.search(patron_total, texto_elemento4)

        iva = match_iva.group(1).replace(",", "") if match_iva else None
        total = match_total.group(1).replace(",", "") if match_total else None

        iva = int(iva) if iva else 0
        total = int(total) if total else 0

    except Exception as e:
        elemento4 = driver.find_element(By.XPATH, "//div[@class='col-md-3'][4]/p[2]")
        texto_elemento4 = elemento4.text

        patron_iva = r"IVA:\s*\$([\d,]+)"
        patron_total = r"Total:\s*\$([\d,]+)"

        match_iva = re.search(patron_iva, texto_elemento4)
        match_total = re.search(patron_total, texto_elemento4)

        iva = match_iva.group(1).replace(",", "") if match_iva else None
        total = match_total.group(1).replace(",", "") if match_total else None

        iva = int(iva) if iva else 0
        total = int(total) if total else 0

        
    ###########################PDF BASE 64 ######################################
    print(f"[DEBUG] Buscando archivo PDF específico: {cufe}.pdf en {ruta_carpeta}")
    
    # Función para esperar descarga de PDF específico con timeout
    def esperar_descarga_pdf_especifico(directorio, nombre_cufe, timeout_segundos=15):
        """Espera hasta que aparezca el archivo PDF específico del CUFE o hasta timeout"""
        import time
        tiempo_inicio = time.time()
        nombre_archivo_esperado = f"{nombre_cufe}.pdf"
        ruta_archivo_esperado = os.path.join(directorio, nombre_archivo_esperado)
        
        print(f"[DEBUG] Esperando archivo: {nombre_archivo_esperado}")
        
        while time.time() - tiempo_inicio < timeout_segundos:
            try:
                # Buscar archivo exacto
                if os.path.exists(ruta_archivo_esperado):
                    print(f"[DEBUG] PDF específico encontrado después de {time.time() - tiempo_inicio:.1f} segundos")
                    return [nombre_archivo_esperado]
                
                # Buscar archivos que contengan el CUFE (incluyendo con sufijos como (1), (2), etc.)
                archivos_pdf = [archivo for archivo in os.listdir(directorio) if archivo.endswith(".pdf")]
                for archivo in archivos_pdf:
                    # Verificar si el archivo contiene el CUFE al inicio
                    if archivo.startswith(nombre_cufe):
                        print(f"[DEBUG] PDF con CUFE encontrado (con sufijo): {archivo}")
                        return [archivo]
                
                if archivos_pdf and tiempo_inicio % 3 == 0:  # Log cada 3 segundos
                    print(f"[DEBUG] PDFs disponibles: {len(archivos_pdf)} archivos, esperando {nombre_archivo_esperado}")
                
            except Exception as e:
                print(f"[DEBUG] Error accediendo a directorio {directorio}: {e}")
                break
            time.sleep(1)  # Esperar 1 segundo entre verificaciones
        
        print(f"[DEBUG] Timeout alcanzado ({timeout_segundos}s) esperando descarga de PDF específico")
        return []
    
    # Esperar a que se descargue el PDF específico del CUFE
    archivos_pdf = esperar_descarga_pdf_especifico(ruta_carpeta, cufe)
    
    print(f"[DEBUG] Archivos PDF encontrados: {len(archivos_pdf)}")
    if archivos_pdf:
        print(f"[DEBUG] Lista de PDFs: {archivos_pdf}")
    
    # Inicializar variable base64_pdf
    base64_pdf = 'No se encontro PDF'

    # Verificar si hay archivos PDF
    if archivos_pdf:
        try:
            # Tomar el primer PDF encontrado
            archivo_pdf = archivos_pdf[0]
            print(f"[DEBUG] Procesando PDF: {archivo_pdf}")
            ruta_pdf2 = os.path.join(ruta_carpeta, archivo_pdf)
            
            # Verificar que el archivo existe y no está vacío
            if os.path.exists(ruta_pdf2) and os.path.getsize(ruta_pdf2) > 0:
                print(f"[DEBUG] Archivo PDF válido, tamaño: {os.path.getsize(ruta_pdf2)} bytes")
                
                # Leer el archivo en modo binario y convertirlo a Base64
                with open(ruta_pdf2, "rb") as archivo:
                    contenido_pdf = archivo.read()
                    base64_pdf = base64.b64encode(contenido_pdf).decode("utf-8")
                
                print(f"[DEBUG] PDF convertido a base64, longitud: {len(base64_pdf)} caracteres")
            else:
                print(f"[ERROR] Archivo PDF no válido o vacío: {ruta_pdf2}")
                base64_pdf = 'PDF vacio o no valido'
                
        except Exception as e:
            print(f"[ERROR] Error procesando PDF: {e}")
            base64_pdf = f'Error procesando PDF: {str(e)}'
    else:
        print(f"[WARNING] No se encontró el archivo PDF específico {cufe}.pdf en la carpeta de descargas")
        # Intentar buscar cualquier PDF como fallback
        try:
            todos_los_pdfs = [archivo for archivo in os.listdir(ruta_carpeta) if archivo.endswith(".pdf")]
            if todos_los_pdfs:
                print(f"[DEBUG] PDFs disponibles como fallback: {todos_los_pdfs}")
            base64_pdf = 'No se encontro PDF especifico'
        except Exception as e:
            print(f"[DEBUG] Error listando PDFs: {e}")
            base64_pdf = 'No se encontro PDF'


    ###########################CREAR JSON ######################################

    # if iva == 0:
    #     iva=1

    # Crear un diccionario con los datos
    datos = {
        "clienteNombre": nombre_cliente_actual,
        "clienteDocumento": documento_cliente_actual,
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
        "clienteNombre": nombre_cliente_actual,
        "clienteDocumento": documento_cliente_actual,
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

    

    # =====================================================
    # ENVIAR DATOS DIRECTAMENTE AL ENDPOINT (SIN ARCHIVO JSON)
    # =====================================================
    # Ya no guardamos en disco - enviamos directamente el objeto datos
    print(f"[INFO] Enviando datos al endpoint para CUFE: {cufe[:20]}...")
    
    # Guardar la información de la factura procesada en un archivo acumulativo TXT (solo para auditoría)
    config_dir = "./config"
    ruta_txt_facturas = os.path.join(config_dir, "facturas_procesadas.txt")
    with open(ruta_txt_facturas, "a", encoding="utf-8") as archivo_txt:
        archivo_txt.write(json.dumps(datos, ensure_ascii=False))
        archivo_txt.write("\n---\n")

    # LLAMADA DIRECTA AL ENDPOINT SIN ARCHIVO INTERMEDIO
    response = post_facturas(datos)
    print("RESPONSE: ", response)
    if not response:
        print("No se obtuvo respuesta del endpoint /facturas. Ver logs para más detalles.")
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | No se obtuvo respuesta del endpoint /facturas. Datos RPA: {datos2} | Fin  Error CUFE: {cufe}!\n"

        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

    try:
        status_code = response.get("status") if isinstance(response, dict) else None
    except Exception:
        status_code = None

    if status_code != 200:
        print("ERROR en endpoint /facturas, status:", status_code)
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Finalizo Registro Factura: {folio} | Fin  Error CUFE: {cufe} RespuestaEmpoint: {response} Datos RPA: {datos2}!\n"
        with open(logerrores, "a", encoding="utf-8") as archivo:
            archivo.write(mensajeerror)
        return None

    print("OK")
    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    mensaje2 = f"FECHA: [{fecha_actual}] | INFO | DescargaRegistro | Finalizo Registro Factura: {folio} | Registro  con exito CUFE: {cufe}  RespuestaEmpoint: {response}!\n"

    with open(logeventos, "a", encoding="utf-8") as archivo:
        archivo.write(mensaje2)

   
    ################################ELIMINAR ARCHIVOS PDF ########################################

    # Eliminar específicamente el PDF del CUFE procesado
    nombre_pdf_cufe = f"{cufe}.pdf"
    ruta_pdf_cufe = os.path.join(ruta_carpeta, nombre_pdf_cufe)
    
    try:
        if os.path.exists(ruta_pdf_cufe):
            time.sleep(1)
            os.remove(ruta_pdf_cufe)
            print(f"[DEBUG] Eliminado PDF específico: {nombre_pdf_cufe}")
        else:
            print(f"[DEBUG] PDF específico no encontrado para eliminar: {nombre_pdf_cufe}")
    except Exception as e:
        print(f"[DEBUG] Error eliminando PDF específico: {e}")
    
    try:
        for archivo in os.listdir(ruta_carpeta):
            if archivo.endswith(".pdf"):
                time.sleep(1)
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                os.remove(ruta_archivo)
                print(f"[DEBUG] Eliminado PDF adicional: {archivo}")
    except Exception as e:
        print(f"[DEBUG] Error en limpieza adicional de PDFs: {e}")

    # PROCESAMIENTO COMPLETADO EXITOSAMENTE
    # Ya no eliminamos filas de Excel, el endpoint maneja el estado

    driver.quit()
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM msedge.exe")
    os.system("taskkill /F /IM firefox.exe")
    os.system("taskkill /F /IM brave.exe")
    os.system("taskkill /f /im chrome.exe")

    print("Salida exitosa")
    # Indicar al llamador que la función terminó correctamente
    return True


