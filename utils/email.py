import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatario: str, assunto: str, corpo: str):
    msg = MIMEText(corpo, "html")
    msg["Subject"] = assunto
    msg["From"] = "sistema@empresa.com"
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.exemplo.com", 587) as server:
        server.starttls()
        server.login("usuario", "senha")
        server.send_message(msg)
