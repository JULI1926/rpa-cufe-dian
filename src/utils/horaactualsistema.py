from datetime import datetime
import pytz

# Zona horaria de Colombia
zona_horaria_colombia = pytz.timezone("America/Bogota")

# Obtener la hora actual en Colombia
hora_actual_colombia = datetime.now(zona_horaria_colombia).strftime("%Y-%m-%d %H:%M:%S")

print(hora_actual_colombia)