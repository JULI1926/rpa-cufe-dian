

import pyautogui
import time

# Coordenadas a las que quieres hacer clic
x = 2691
y = 449

print("Haciendo clic en 5 segundos...")
time.sleep(5)  # Te da tiempo de ver a dónde va a hacer clic

# Mueve el mouse y hace clic
pyautogui.click(x, y)

print(f"Se hizo clic en ({x}, {y})")

