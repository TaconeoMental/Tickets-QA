#!/usr/bin/python3

FLAG = "MAGIA{XXX}"

from sys import stdin
import json
import string
import random
import jinja2
import mailparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

MAIL_FROM = "solicitud@dominioreal.xyz"

def sendmail(user_email, body):
    msg = MIMEMultipart()
    msg['Subject'] = "Comprobante Solicitud"
    msg['From'] = MAIL_FROM
    msg['To'] = user_email
    # TODO: Ver cómo integramos credenciales/tokens de autorización entre
    # componentes
    msg.attach(MIMEText(body))
    with SMTP("localhost") as smtp:
        smtp.login("USERFALSO", "PASSFALSA")
        smtp.sendmail(MAIL_FROM, user_email, msg.as_string())

def write(user_email, body):
    with open("/tmp/xd", "a") as f:
        f.write(user_email + "/n" + body)

def main():
    # Leemos el mensaje desde stdin (viene de postfix)
    raw_message = str()
    for line in stdin:
        raw_message += line

    # Sacamos el cuerpo y lo transformamos en un diccionario
    mail = mailparser.parse_from_string(raw_message)
    info_dict = json.loads(mail.body.strip(), strict=False)

    # Creamos el template
    message_template = jinja2.Template(info_dict["template"])

    # Generamos el código de solicitud
    codigo_sol = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Renderizamos el template y lo enviamos
    sendmail(info_dict["email"], message_template.render(
        codigo=codigo_sol,
        flag=FLAG
    ))

if __name__ == "__main__":
    main()
