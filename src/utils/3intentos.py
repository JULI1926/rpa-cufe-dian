"""
Módulo para automatización de descarga de documentos DIAN con resolución automática de CAPTCHA.
Incluye manejo de reintentos y fallbacks para mayor robustez.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
from datetime import datetime
import os
import sys

# Configuración de constantes
DIAN_URL = 'https://catalogo-vpfe.dian.gov.co/User/SearchDocument'
XPATH_DOCUMENT_KEY = '//*[@id="DocumentKey"]'
XPATH_SEARCH_BUTTON = '//*[@id="search-document-form"]/button'
XPATH_DOWNLOAD_BUTTON = "(//a[@class='downloadPDFUrl'])[1]"
MAX_DOWNLOAD_RETRIES = 3


class DianConfig:
    """Configuración para el procesamiento DIAN"""
    
    def __init__(self):
        self.fecha_actual = datetime.now().strftime('%Y%m%d')
        self.descargas = "./downloads"
        self.rutaimagen = "./config/catchat.png"
        self.base_logs = "./logs"
        self.nombrecliente = 'Alejandro Bustos'
        self.documentocliente = '1054990077'
        
        # Crear directorios si no existen
        os.makedirs(self.base_logs, exist_ok=True)
        
        # Configurar rutas de logs
        self.logeventos = os.path.join(self.base_logs, f"LogEventos{self.fecha_actual}.txt")
        self.logerrores = os.path.join(self.base_logs, f"LogErrores{self.fecha_actual}.txt")
        
        print(f"Ruta de Descargas: {self.descargas}")


class LogManager:
    """Manejo de logs para el procesamiento"""
    
    @staticmethod
    def escribir_log_evento(archivo_log, mensaje):
        """Escribir un evento en el archivo de log"""
        fecha_actual = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT-0500 (hora estándar de Colombia)")
        mensaje_completo = f"FECHA: [{fecha_actual}] | INFO | {mensaje}\n"
        
        try:
            with open(archivo_log, "a", encoding="utf-8") as archivo:
                archivo.write(mensaje_completo)
        except Exception as e:
            print(f"Error escribiendo log: {e}")


class ChromeDriverManager:
    """Manejo del driver de Chrome con configuración optimizada"""
    
    @staticmethod
    def crear_driver():
        """Crear una instancia del driver de Chrome con configuración optimizada"""
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
        
        return webdriver.Chrome(options=options)


class CaptchaResolver:
    """Resolutor de CAPTCHA con múltiples estrategias"""
    
    @staticmethod
    def detect_and_click_captcha(driver, image_path, retries=3, pause=2, use_opencv_fallback=True, allow_manual=True):
        """
        Intentar localizar y clickear la plantilla en pantalla.
        
        Args:
            driver: Instancia del WebDriver
            image_path: Ruta de la imagen del captcha
            retries: Número de reintentos
            pause: Pausa entre reintentos
            use_opencv_fallback: Usar OpenCV como fallback
            allow_manual: Permitir intervención manual
            
        Returns:
            bool: True si fue clickeada, False en caso contrario
        """
        region = CaptchaResolver._get_browser_region(driver)
        
        # Estrategia 1: PyAutoGUI
        if CaptchaResolver._try_pyautogui_detection(image_path, retries, pause, region):
            return True
        
        # Estrategia 2: OpenCV fallback
        if use_opencv_fallback and CaptchaResolver._try_opencv_detection(image_path, region):
            return True
        
        # Estrategia 3: Intervención manual
        if allow_manual:
            return CaptchaResolver._manual_intervention()
        
        return False
    
    @staticmethod
    def _get_browser_region(driver):
        """Obtener la región de la ventana del navegador"""
        try:
            rect = driver.get_window_rect()
            win_left = int(rect.get('x', 0))
            win_top = int(rect.get('y', 0))
            win_width = int(rect.get('width', 0))
            win_height = int(rect.get('height', 0))
            
            # Reducir la región un poco (margen) para evitar barras/frames
            margin_w = max(20, win_width // 20)
            margin_h = max(20, win_height // 20)
            
            return (
                win_left + margin_w, 
                win_top + margin_h, 
                max(50, win_width - 2 * margin_w), 
                max(50, win_height - 2 * margin_h)
            )
        except Exception as e:
            print(f"Error obteniendo región del navegador: {e}")
            return None
    
    @staticmethod
    def _try_pyautogui_detection(image_path, retries, pause, region):
        """Intentar detección con PyAutoGUI"""
        try:
            for i in range(retries):
                try:
                    if region:
                        pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.8, region=region)
                    else:
                        pos = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

                    if pos:
                        pyautogui.click(pos)
                        print(f"Imagen encontrada y clickeada (pyautogui) en intento {i+1} -> pos={pos}")
                        return True
                        
                except Exception as e:
                    print(f"PyAutoGUI intento {i+1} falló: {e}")
                
                time.sleep(pause)
                
        except Exception as e:
            print(f"Error en detección PyAutoGUI: {e}")
        
        return False
    
    @staticmethod
    def _try_opencv_detection(image_path, region):
        """Intentar detección con OpenCV"""
        try:
            import cv2
            import numpy as np
            
            print("Intentando fallback OpenCV (region-aware)...")
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            
            if template is None:
                print("OpenCV: no pudo leer la plantilla, verificar ruta")
                return False
            
            w, h = template.shape[1], template.shape[0]
            
            # Tomar screenshot y procesar
            if region:
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
            print(f"OpenCV fallback no disponible o falló: {e}")
        
        return False
    
    @staticmethod
    def _manual_intervention():
        """Permitir intervención manual del usuario"""
        print("No se pudo detectar automáticamente el captcha. Pausando para intervención humana.")
        print("Por favor, resuelve el CAPTCHA manualmente y presiona ENTER para continuar, o escribe 'skip' para saltar.")
        
        respuesta = input().strip().lower()
        if respuesta == 'skip':
            print("Usuario solicitó omitir el captcha manualmente.")
            return False
        else:
            print("Usuario confirmó resolución manual del captcha.")
            return True


class DianProcessor:
    """Procesador principal para documentos DIAN"""
    
    def __init__(self, config):
        self.config = config
        self.driver = None
    
    def procesar_cufe(self, cufe):
        """
        Procesar un CUFE específico
        
        Args:
            cufe (str): El CUFE a procesar
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        print(f"Iniciando procesamiento de CUFE: {cufe}")
        
        # Escribir log de inicio
        LogManager.escribir_log_evento(
            self.config.logeventos, 
            f"IniciarRegistro | Inicio tarea | CUFE: {cufe}"
        )
        
        try:
            # Inicializar driver
            self.driver = ChromeDriverManager.crear_driver()
            
            # Navegar a la página DIAN
            if not self._navegar_a_dian():
                return False
            
            # Completar formulario
            if not self._completar_formulario(cufe):
                return False
            
            # Descargar documento
            if not self._descargar_documento():
                return False
            
            print("Procesamiento completado exitosamente")
            return True
            
        except Exception as e:
            print(f"Error inesperado durante el procesamiento: {e}")
            LogManager.escribir_log_evento(
                self.config.logerrores, 
                f"Error inesperado: {str(e)}"
            )
            return False
            
        finally:
            self._cleanup()
    
    def _navegar_a_dian(self):
        """Navegar a la página de DIAN"""
        try:
            print("Navegando a página DIAN...")
            self.driver.execute_script(f"window.open('{DIAN_URL}', '_blank')")
            time.sleep(15)
            self.driver.switch_to.window(self.driver.window_handles[1])
            print("Página DIAN cargada")
            
            # Manejar frame si existe
            try:
                self.driver.switch_to.frame(0)
                print("Frame encontrado")
            except:
                print('No se encontró frame')
            
            return True
            
        except Exception as e:
            print(f"Error navegando a DIAN: {e}")
            return False
    
    def _completar_formulario(self, cufe):
        """Completar el formulario con el CUFE y resolver CAPTCHA con reintentos"""
        max_retries = 5
        
        for attempt in range(max_retries):
            print(f"[INFO] Intento {attempt + 1}/{max_retries} para procesar CUFE: {cufe[:20]}...")
            
            try:
                # Limpiar campo antes de ingresar CUFE
                input_field = self.driver.find_element(By.XPATH, XPATH_DOCUMENT_KEY)
                input_field.clear()
                input_field.send_keys(cufe)
                print(f"CUFE ingresado: {cufe}")
                
                # Resolver CAPTCHA
                captcha_resuelto = CaptchaResolver.detect_and_click_captcha(
                    self.driver, 
                    self.config.rutaimagen,
                    retries=3,
                    pause=2,
                    use_opencv_fallback=True,
                    allow_manual=False  # No permitir manual en reintentos automáticos
                )
                
                if captcha_resuelto:
                    print(f"[SUCCESS] CAPTCHA resuelto en intento {attempt + 1}")
                    
                    # Hacer clic en buscar
                    time.sleep(2)
                    search_button = self.driver.find_element(By.XPATH, XPATH_SEARCH_BUTTON)
                    search_button.click()
                    print("Búsqueda iniciada")
                    
                    # Verificar si el documento existe
                    time.sleep(4)
                    try:
                        error_element = self.driver.find_element(By.XPATH, '//*[@id="search-document-form"]/div[2]/span')
                        error_text = error_element.text
                        if "Documento no encontrado" in error_text:
                            print("[INFO] CUFE no encontrado en registros de DIAN")
                            LogManager.escribir_log_evento(
                                self.config.logerrores, 
                                f"CUFE no encontrado: {cufe}"
                            )
                            return False
                    except Exception:
                        # No se encontró mensaje de error, continuar
                        pass
                    
                    return True
                else:
                    print(f"[WARNING] CAPTCHA no resuelto en intento {attempt + 1}")
                    if attempt < max_retries - 1:
                        # Refrescar página para reintentar
                        print("[INFO] Refrescando página para reintentar...")
                        self.driver.get(DIAN_URL)
                        time.sleep(3)
                        continue
                    else:
                        print("[ERROR] Máximo número de reintentos alcanzado para CAPTCHA")
                        
            except Exception as e:
                print(f"[ERROR] Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    try:
                        # Intentar refrescar la página
                        self.driver.get(DIAN_URL)
                        time.sleep(3)
                    except Exception as refresh_error:
                        print(f"[ERROR] Error refrescando página: {refresh_error}")
                    continue
                else:
                    print("[ERROR] Máximo número de reintentos alcanzado")
        
        # Si llegamos aquí, todos los reintentos fallaron
        LogManager.escribir_log_evento(
            self.config.logerrores, 
            f"CAPTCHA no pudo ser resuelto después de {max_retries} intentos: {cufe}"
        )
        return False
    
    def _descargar_documento(self):
        """Intentar descargar el documento con reintentos"""
        print("Iniciando descarga de documento...")
        
        for intento in range(1, MAX_DOWNLOAD_RETRIES + 1):
            try:
                time.sleep(2)
                download_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATH_DOWNLOAD_BUTTON))
                )
                download_button.click()
                print(f"Documento descargado correctamente en intento {intento}")
                return True
                
            except Exception as e:
                print(f"Intento {intento} de descarga falló: {e}")
                if intento == MAX_DOWNLOAD_RETRIES:
                    print(f"Falló tras {MAX_DOWNLOAD_RETRIES} intentos")
                    return False
        
        return False
    
    def _cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            try:
                self.driver.quit()
                print("Driver cerrado correctamente")
            except Exception as e:
                print(f"Error cerrando driver: {e}")


def main():
    """Función principal para ejecución directa del script"""
    # CUFE de ejemplo para pruebas
    cufe_prueba = 'a3ff355c946a700da27914344579ff3a72785361909a449303a3788314ae1a9614dd75e2d88981fa294404579a569d59'
    
    # Crear configuración
    config = DianConfig()
    
    # Crear procesador
    processor = DianProcessor(config)
    
    # Procesar CUFE
    exito = processor.procesar_cufe(cufe_prueba)
    
    if exito:
        print("✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("❌ Proceso falló")
        sys.exit(1)


def procesar_cufe_con_configuracion(cufe, config_personalizada=None):
    """
    Función pública para procesar un CUFE con configuración personalizada
    
    Args:
        cufe (str): El CUFE a procesar
        config_personalizada (DianConfig, optional): Configuración personalizada
        
    Returns:
        bool: True si el procesamiento fue exitoso
    """
    config = config_personalizada if config_personalizada else DianConfig()
    processor = DianProcessor(config)
    return processor.procesar_cufe(cufe)


if __name__ == "__main__":
    main()
