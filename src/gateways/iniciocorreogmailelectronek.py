import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
from datetime import datetime
import json


def main(rutajson_param):
    # Usar el parámetro pasado directamente
    rutajson = rutajson_param

    # Leer el archivo JSON
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

    # Configuración del servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Crear el objeto MIMEMultipart para el mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente_email
    mensaje['To'] = ", ".join(destinatario_email)  # Unir los correos con comas
    #mensaje["To"] = destinatario_email
    mensaje["Subject"] = "Proceso DIAN Inicio"

    # Cuerpo del mensaje
    cuerpo_mensaje = "Inicio Proceso Navegacion Pagina DIAN Fecha Ejecucion: "+ fecha
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


if __name__ == "__main__":
    # Para compatibilidad con ejecución directa
    if len(sys.argv) > 1:
        rutajson = os.path.abspath(sys.argv[1])
        main(rutajson)
    else:
        print("Error: No se proporcionó parámetro rutajson")
