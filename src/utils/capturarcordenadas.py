import pyautogui
import time

print("Tienes 5 segundos para mover el mouse a la posición deseada...")
time.sleep(5)

# Obtiene la posición actual del mouse
x, y = pyautogui.position()
print(f"Coordenadas del mouse: ({x}, {y})")


