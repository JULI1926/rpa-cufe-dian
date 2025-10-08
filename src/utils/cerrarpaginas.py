


import pygetwindow as gw
import pyautogui
import time

# Buscar todas las ventanas de Chrome
windows = gw.getWindowsWithTitle(' - Google Chrome')

for window in windows:
    if 'data:,' in window.title:
        # Activar la ventana
        window.activate()
        time.sleep(1)  # Espera a que se active
        # Enviar Ctrl+W para cerrarla
        pyautogui.hotkey('ctrl', 'w')
        print(f'Pestaña cerrada: {window.title}')
        break
else:
    print("No se encontró ninguna pestaña con 'data:,' en el título.")



