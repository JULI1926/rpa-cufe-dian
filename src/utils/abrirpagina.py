# ...existing code...
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import os

# Configurar opciones del navegador
options = Options()
#options.add_experimental_option("detach", True)  # ✅ Mantiene el navegador abierto al final
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-extensions')
options.add_argument('--no-sandbox')
options.add_argument('--disable-infobars')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-browser-side-navigation')
options.add_argument('--disable-gpu')

# Inicializar el servicio y el navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Maximizar la ventana
driver.maximize_window()

# Abrir una nueva pestaña con la URL deseada
driver.execute_script("window.open('https://catalogo-vpfe.dian.gov.co/User/SearchDocument', '_blank')")

# NO BAJAR TIEMPO DE 15 SEGUNDOS
time.sleep(25)

import cv2
import numpy as np
import pyautogui

# Cargar imagen de plantilla
template = cv2.imread('DIAN/catchat.png', cv2.IMREAD_COLOR)
if template is None:
    print("❌ Plantilla 'DIAN/catchat.png' no encontrada. Verifica la ruta del archivo.")
    # Cierra el navegador y registra el evento de forma segura si es posible
    try:
        driver.quit()
    except Exception:
        pass

    fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
    cufe_val = globals().get('cufe', 'N/A')
    mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Plantilla no encontrada | Fin  Error CUFE: {cufe_val} !\n"

    log_path = globals().get('logerrores')
    if log_path:
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as archivo:
                archivo.write(mensajeerror)
        except Exception as e:
            print("No se pudo escribir en logerrores:", e)
            print(mensajeerror)
    else:
        print(mensajeerror)
else:
    w, h = template.shape[1], template.shape[0]

    # Capturar pantalla
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Usar coincidencia de plantilla
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # Umbral de coincidencia
    threshold = 0.8
    if max_val >= threshold:
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        pyautogui.click(center_x, center_y)
        print("✔️ Click realizado con OpenCV.")
    else:
        print("❌ No se encontró la imagen con OpenCV.")
        try:
            driver.quit()
        except Exception:
            pass

        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        cufe_val = globals().get('cufe', 'N/A')
        mensajeerror = f"FECHA: [{fecha_actual}] | WARN | ErrorRegistroFactura | Imagen No encontrada Catchat Try: | Fin  Error CUFE: {cufe_val} !\n"

        log_path = globals().get('logerrores')
        if log_path:
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as archivo:
                    archivo.write(mensajeerror)
            except Exception as e:
                print("No se pudo escribir en logerrores:", e)
                print(mensajeerror)
        else:
            print(mensajeerror)
# ...existing code...