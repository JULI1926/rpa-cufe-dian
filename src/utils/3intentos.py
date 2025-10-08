from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
from datetime import datetime
import os
import sys

# Importar utilidades de rutas
from path_utils import get_downloads_path, get_logs_dir, get_absolute_path

# Obtener la fecha actual en formato YYYYMMDD
fecha_actual = datetime.now().strftime('%Y%m%d')

#RUTAS ARCHIVOS usando utilidades
descargas = get_downloads_path()
print("Ruta de Descargas:", descargas)
# Ruta del archivo PDF
#ruta_pdf = "DIAN/documento.pdf"
rutaimagen = get_absolute_path("config/catchat.png")
# Ruta donde se encuentran los archivos PDF
ruta_carpeta = descargas
nombrecliente='Alejandro Bustos'
documentocliente='1054990077'
# RUTA LOGS: usar utilidades de rutas
base_logs = get_logs_dir()
os.makedirs(base_logs, exist_ok=True)
logeventos = os.path.join(base_logs, f"LogEventos{fecha_actual}.txt")
logerrores = os.path.join(base_logs, f"LogErrores{fecha_actual}.txt")
# logeventos="DIAN/LogEventos.txt"
# logerrores="DIAN/LogErrores.txt"
cufeexcel='a3ff355c946a700da27914344579ff3a72785361909a449303a3788314ae1a9614dd75e2d88981fa294404579a569d59'

# Obtener la fecha y hora actual en el formato deseado
fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
# Crear el mensaje de log
mensaje = f"FECHA: [{fecha_actual}] | INFO | IniciarRegistro | Inicio tarea | Inicio  con exito!\n"
# Guardar el mensaje en el archivo (modo 'a' para añadir sin borrar)
with open(logeventos, "a", encoding="utf-8") as archivo:
    archivo.write(mensaje)

# FUNCION NAVEGACION
#def procesarfactura(cufeexcel):
# Configuración de opciones para la navegación
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

# Inicia el navegador
driver = webdriver.Chrome(options=options)

try:
    # Abre la página
    driver.execute_script("window.open('https://catalogo-vpfe.dian.gov.co/User/SearchDocument', '_blank')")
    time.sleep(15)
    driver.switch_to.window(driver.window_handles[1])
    print("Buscando página")

    # Maneja el frame
    try:
        driver.switch_to.frame(0)
        print("Frame encontrado")
    except:
        print('No frame encontrado')

    # Ingresa el CUFE
    cufe = cufeexcel
    input_field = driver.find_element(By.XPATH, '//*[@id="DocumentKey"]')
    input_field.send_keys(cufe)
    # Localiza la imagen del CAPTCHA con retries y fallback
    def detect_and_click_captcha(image_path, retries=3, pause=2, use_opencv_fallback=True, allow_manual=True):
        """Intentar localizar y clickear la plantilla en pantalla.
        - Primero intenta pyautogui.locateCenterOnScreen con el confidence indicado varias veces.
        - Si falla y OpenCV está disponible, intenta matchTemplate como fallback.
        - Si sigue fallando y allow_manual=True, pausa y permite intervención humana.
        Retorna True si fue clickeada, False en caso contrario.
        """
        # Intentar detectar usando la región de la ventana del navegador para acelerar
        try:
            # Obtener posición y tamaño de la ventana del navegador si driver está disponible
            win_left = win_top = win_width = win_height = None
            try:
                rect = driver.get_window_rect()
                win_left = int(rect.get('x', 0))
                win_top = int(rect.get('y', 0))
                win_width = int(rect.get('width', 0))
                win_height = int(rect.get('height', 0))
                # Reducir la región un poco (margen) para evitar barras/frames
                margin_w = max(20, win_width // 20)
                margin_h = max(20, win_height // 20)
                region = (win_left + margin_w, win_top + margin_h, max(50, win_width - 2 * margin_w), max(50, win_height - 2 * margin_h))
            except Exception:
                region = None

            for i in range(retries):
                try:
                    if region:
                        # Usar screenshot de la región para localizar más rápido
                        screenshot = pyautogui.screenshot(region=region)
                        pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.8, region=region)
                    else:
                        pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

                    if pos:
                        pyautogui.click(pos)
                        print(f"Imagen encontrada y clickeada (pyautogui) en intento {i+1} -> pos={pos}")
                        return True
                except Exception as e:
                    # pyautogui may raise if screenshot access is blocked; keep trying
                    print(f"pyautogui intento {i+1} fallo: {e}")
                time.sleep(pause)
        except Exception as e:
            print("Error preparando búsqueda por región:", e)

        # Fallback using OpenCV template matching if available
        if use_opencv_fallback:
            try:
                import cv2
                import numpy as np
                print("Intentando fallback OpenCV (region-aware)...")
                template = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if template is None:
                    print("OpenCV: no pudo leer la plantilla, verificar ruta")
                else:
                    w, h = template.shape[1], template.shape[0]
                    # Si tenemos region, tomar screenshot sólo de esa región
                    if 'region' in locals() and region is not None:
                        sx, sy, sw, sh = region
                        screenshot = pyautogui.screenshot(region=region)
                        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        threshold = 0.72
                        if max_val >= threshold:
                            center_x = sx + max_loc[0] + w // 2
                            center_y = sy + max_loc[1] + h // 2
                            pyautogui.click(center_x, center_y)
                            print(f"Imagen encontrada y clickeada (OpenCV region) con score {max_val}")
                            return True
                        else:
                            print(f"OpenCV region match score {max_val} < {threshold}")
                    else:
                        screenshot = pyautogui.screenshot()
                        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        threshold = 0.75
                        if max_val >= threshold:
                            center_x = max_loc[0] + w // 2
                            center_y = max_loc[1] + h // 2
                            pyautogui.click(center_x, center_y)
                            print(f"Imagen encontrada y clickeada (OpenCV) con score {max_val}")
                            return True
                        else:
                            print(f"OpenCV match score {max_val} < {threshold}")
            except Exception as e:
                print("OpenCV fallback no disponible o falló:", e)

        # Manual intervention fallback
        if allow_manual:
            print("No se pudo detectar automáticamente el captcha. Pausando para intervención humana.")
            print("Por favor, resuelve el CAPTCHA manualmente y presiona ENTER para continuar, o escribe 'skip' para saltar.")
            respuesta = input().strip().lower()
            if respuesta == 'skip':
                print("Usuario solicitó omitir el captcha manualmente.")
                return False
            else:
                # Asumimos que el usuario resolvió el captcha
                return True

        return False

    captcha_ok = detect_and_click_captcha(rutaimagen, retries=3, pause=2, use_opencv_fallback=True, allow_manual=True)
    if not captcha_ok:
        print("Imagen CAPTCHA no resuelta; abortando intento actual.")
        driver.quit()
        sys.exit(1)

    # Dar clic en el botón de búsqueda
    time.sleep(2)
    search_button = driver.find_element(By.XPATH, '//*[@id="search-document-form"]/button')
    search_button.click()

    # Intentar dar clic en el botón de descarga hasta 3 veces
    intento = 0
    exito = False

    while intento < 3 and not exito:
        try:
            time.sleep(2)
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[@class='downloadPDFUrl'])[1]"))
            )
            download_button.click()
            print("Documento descargado correctamente")
            exito = True

        except Exception as e:
            intento += 1
            print(f"Intento {intento} fallido: {e}")

    # Si no tuvo éxito después de 3 intentos, reinicia el navegador
    if not exito:
        print("Fallo tras 3 intentos. Reiniciando navegador...")
        driver.quit()
        #procesarfactura(cufeexcel)  # Reinicia la función desde cero

except Exception as e:
    print(f"Error inesperado: {e}")
    driver.quit()

finally:
    # Cerrar el navegador al terminar
    driver.quit()
