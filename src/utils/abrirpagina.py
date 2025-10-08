from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyautogui


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

# pyautogui.doubleClick(1093, 688)  #Doble clic en (500, 300)
# print("dio click")
# # NO BAJAR TIEMPO DE 15 SEGUNDOS
# time.sleep(15)

#pyautogui.doubleClick(1093, 688)  #Doble clic en (500, 300)
# import pyautogui
# import time

# # Espera unos segundos para que cargue la página
# time.sleep(5)

# # Ruta de la imagen del checkbox
# ruta = "DIAN/catchat.png"

# # Busca la posición de la imagen en pantalla
# pos = pyautogui.locateCenterOnScreen(ruta, confidence=0.8, grayscale=True)

# # Si encuentra la imagen, hace clic
# if pos:
#     pyautogui.moveTo(pos)
#     pyautogui.click()
#     print("✔️ Click realizado en el CAPTCHA.")
# else:
#     print("❌ Imagen no encontrada.")


import cv2
import numpy as np
import pyautogui

# Cargar imagen de plantilla
template = cv2.imread('DIAN/catchat.png', cv2.IMREAD_COLOR)
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
