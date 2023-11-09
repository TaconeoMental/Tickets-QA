from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from smtplib import SMTP
import time

import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, render_template, request, send_file

# No está listo para producción!!!!
# Correr con gunicorn -w 10 -b 0.0.0.0:80 --daemon app:app
# :)

app = Flask(__name__)
rate_limiter = Limiter(app=app, key_func=get_remote_address)

DOMINIO = "dominioreal.xyz"
MAIL_FROM = f"webform@{DOMINIO}"
RCPT_TO = f"solicitud@{DOMINIO}"

TEMPLATE = """\
Hola, {}

Gracias por tu solicitud, nos contactaremos pronto contigo.
Este es tu código de seguimiento: {{{{ codigo }}}}

Esta es una copia de tu mensaje:
-------------------------------
{}
-------------------------------

Saludos,
Equipo de Dominio Real.
"""

def sendmail(body):
    msg = MIMEMultipart()
    msg['Subject'] = f"Webform - {time.ctime()}"
    msg['From'] = MAIL_FROM
    msg['To'] = RCPT_TO
    msg.attach(MIMEText(body))
    with SMTP("192.155.95.27") as smtp:
        smtp.helo("dominioreal.xyz")
        smtp.sendmail(MAIL_FROM, RCPT_TO, msg.as_string())

def process_ticket(name, email, message):
    # Esto es seguro?
    final_template = TEMPLATE.format(name, message)

    # Al final el servidor de correo recibe un mensaje con dos valores: el
    # template y un correo. Luego, va a renderizar el template y enviarlo a
    # dicho correo
    json_str = json.dumps({
        "template": final_template,
        "email": email
    })
    sendmail(json_str)

# Formulario HTML
@app.route("/")
def main():
    return render_template('index.html')

@app.route("/", methods=["POST"])
@rate_limiter.limit("10/minute")
def handle_form():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if all([name, email, message]):
        process_ticket(name, email, message)
    return flask.make_response(flask.redirect("/"))

if __name__ == "__main__":
    app.run()
