import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
from datetime import datetime
import json
import getpass

usuario = getpass.getuser()
print("Usuario del equipo:", usuario)


#TRAEMOS LA RUTA DESDE ELECTRONEEK VARIABLE COMO RUTA PYTHON
lote = os.path.abspath(sys.argv[1])
# Normalizar: si se pasa una ruta por error (p. ej. desde un runner), quedarnos con el basename
try:
    lote = os.path.basename(lote)
except Exception:
    # si por alguna razón basename falla, mantener el valor absoluto
    pass

# Leer el archivo JSON
rutajson=r'C:/Users/julia/Desktop/VALIDACIONES_DIAN/DIAN/VariablesGlobales.json'

with open(rutajson, 'r') as archivo:
    datos = json.load(archivo)

# Acceder al primer elemento de la lista
primer_objeto = datos[0]  # Asegúrate de que el JSON tiene al menos un objeto

# Asignar los valores a variables
remitente_email = primer_objeto['correorpa']
remitente_password = primer_objeto['contrasenarpa']
destinatario_email = primer_objeto['destinatario']

#FECHA ACTUAL DEL SISTEMA
fecha = datetime.now()
#PASAMOS DE TIPO DATE A STRING
fecha=str(fecha)
#SEPARAMOS LA FECHA 
separador=fecha.split(" ")
#OBTENEMOS LA POSICION DE LA FECHA
fechas=separador[0]

# #Variables
# remitente_email = "rpa@mercaldas.com.co"
# remitente_password = "kpbr fppu zbre djpi"
# destinatario_email = ["jbustos@cyt.com.co","vfranco@cyt.com.co","mgonzalez@cyt.com.co","enrutador03@mercaldas.com.co","enrutador02@mercaldas.com.co","coordinadorfe@mercaldas.com.co","jcastano@mercaldas.com.co","mejaramillo@mercaldas.com.co"]
# #destinatario_email = ["jbustos@cyt.com.co","amcastano@cyt.com.co"]

# Configuración del servidor SMTP de Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Crear el objeto MIMEMultipart para el mensaje
mensaje = MIMEMultipart()
mensaje["From"] = remitente_email
mensaje['To'] = ", ".join(destinatario_email)  # Unir los correos con comas
#mensaje["To"] = destinatario_email
mensaje["Subject"] = "Proceso DIAN Fin"

# Cuerpo del mensaje
cuerpo_mensaje = "Fin Proceso Navegacion Pagina DIAN Fecha Ejecucion: "+ fecha + " LOTE: "+ lote
mensaje.attach(MIMEText(cuerpo_mensaje, "plain"))

# Conectar al servidor SMTP y enviar el mensaje
try:
    servidor_smtp = smtplib.SMTP(smtp_server, smtp_port)
    servidor_smtp.starttls()  # Habilitar el modo seguro (TLS)
    servidor_smtp.login(remitente_email, remitente_password)
    servidor_smtp.sendmail(remitente_email, destinatario_email, mensaje.as_string())
    servidor_smtp.quit()
    print("Correo enviado exitosamente Python.")
except Exception as e:
    print("Error al enviar el correo: Python", e)
