import pyautogui
import time
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_and_click_image(driver, image_path, retries=3, pause=1, confidence=0.8, use_opencv_fallback=True, allow_manual=True):
    """Buscar y clicar una imagen en pantalla limitada a la ventana del navegador.
    - driver: instancia de selenium webdriver (para obtener rect de ventana)
    - image_path: ruta a la plantilla
    - retries, pause: reintentos y pausa entre ellos
    - confidence: confianza para pyautogui
    - use_opencv_fallback: si True intenta OpenCV como fallback
    - allow_manual: si True permite intervención manual
    Retorna True si se hizo clic, False en caso contrario.
    """
    region = None
    try:
        rect = driver.get_window_rect()
        win_left = int(rect.get('x', 0))
        win_top = int(rect.get('y', 0))
        win_width = int(rect.get('width', 0))
        win_height = int(rect.get('height', 0))
        margin_w = max(20, win_width // 20)
        margin_h = max(20, win_height // 20)
        region = (win_left + margin_w, win_top + margin_h, max(50, win_width - 2 * margin_w), max(50, win_height - 2 * margin_h))
    except Exception:
        region = None

    # Intento con pyautogui (region-aware)
    for i in range(retries):
        try:
            if region:
                pos = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=region)
            else:
                pos = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)

            if pos:
                pyautogui.click(pos)
                print(f"Imagen encontrada y clickeada (pyautogui) en intento {i+1} -> pos={pos}")
                return True
        except Exception as e:
            print(f"pyautogui intento {i+1} fallo: {e}")
        time.sleep(pause)

    # Fallback OpenCV
    if use_opencv_fallback:
        try:
            import cv2
            import numpy as np
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is None:
                print("OpenCV: no pudo leer la plantilla, verificar ruta")
            else:
                w, h = template.shape[1], template.shape[0]
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
            print("OpenCV fallback no disponible o falló:", e)

    # Manual fallback
    if allow_manual:
        print("No se pudo detectar automáticamente la imagen. Pausando para intervención humana.")
        print("Por favor, resuelve manualmente y presiona ENTER para continuar, o escribe 'skip' para saltar.")
        respuesta = input().strip().lower()
        if respuesta == 'skip':
            print("Usuario solicitó omitir la acción manualmente.")
            return False
        else:
            return True

    return False


def try_click_via_dom(driver, timeout=2):
    """Intentar hacer click en el captcha vía DOM/JS. Retorna True si hizo click."""
    start = time.perf_counter()
    try:
        # intentamos detectar iframe primero (si existe)
        try:
            iframe = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            driver.switch_to.frame(iframe)
        except Exception:
            pass

        selectors = [
            'input[type="checkbox"]',
            '#recaptcha-anchor',
            '.recaptcha-checkbox',
            '.captcha-checkbox',
            'label[for^="captcha"]',
        ]
        for sel in selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elems:
                    try:
                        if el.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", el)
                            try:
                                driver.switch_to.default_content()
                            except Exception:
                                pass
                            print(f"Clicked via DOM selector {sel} in {time.perf_counter()-start:.2f}s")
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
    except Exception as e:
        print('try_click_via_dom error:', e)
    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
    return False
