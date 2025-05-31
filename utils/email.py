import secrets
import smtplib
from email.mime.text import MIMEText
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_token():
    return secrets.token_urlsafe(32)

def enviar_email_reset(destinatario, link):
    corpo = f"Clique no link para trocar sua senha: <a href='{link}'>Redefinir Senha</a>"
    msg = MIMEText(corpo, 'html')
    msg['Subject'] = 'Recuperação de Senha'
    msg['From'] = 'sistema@exemplo.com'
    msg['To'] = destinatario

    with smtplib.SMTP('smtp.exemplo.com', 587) as server:
        server.starttls()
        server.login('usuario', 'senha')
        server.send_message(msg)
