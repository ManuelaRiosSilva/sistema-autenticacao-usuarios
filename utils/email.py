import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_token():
    return secrets.token_urlsafe(32)

def enviar_email_reset(destinatario: str, link: str):
    from smtplib import SMTP
    from email.mime.text import MIMEText

    msg = MIMEText(f"Clique no link para redefinir sua senha: {link}")
    msg['Subject'] = "Redefinição de Senha"
    msg['From'] = "recuperacao-senha@gmail.com"
    msg['To'] = destinatario

    with SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("manuela.rios.silva@gmail.com", "txicudqdcbzxeeru")
        server.send_message(msg)


