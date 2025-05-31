from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from models import Usuario, TokenReset
from schemas import EsqueciSenhaRequest, NovaSenhaRequest
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from auth import verificar_senha, criar_token_jwt
from utils.email import enviar_email
import secrets
import re

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    senha = form_data.password

    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário inexistente")

    if not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    token = criar_token_jwt(usuario.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/esqueci_senha")
def esqueci_senha(req: EsqueciSenhaRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == req.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    token = secrets.token_urlsafe(32)
    expira = datetime.utcnow() + timedelta(hours=1)
    novo_token = TokenReset(token=token, usuario_id=usuario.id, expira_em=expira)
    db.add(novo_token)
    db.commit()

    link = f"http://127.0.0.1:8000/frontend/nova_senha.html?token={token}"
    corpo = f"""
        <p>Olá {usuario.nome},</p>
        <p>Recebemos sua solicitação de redefinição de senha. Clique no botão abaixo:</p>
        <a href="{link}" style="padding: 10px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Redefinir Senha</a>
    """
    enviar_email(destinatario=usuario.email, assunto="Redefinição de senha", corpo=corpo)
    return {"mensagem": "Email enviado com sucesso"}

def senha_forte(s: str) -> bool:
    return (len(s) >= 8 and re.search(r"[A-Z]", s) and re.search(r"[a-z]", s)
            and re.search(r"\d", s) and re.search(r"[^\w\s]", s))

@router.post("/nova_senha")
def nova_senha(dados: NovaSenhaRequest, db: Session = Depends(get_db)):
    token = db.query(TokenReset).filter(TokenReset.token == dados.token).first()
    if not token or token.expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter(Usuario.id == token.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not senha_forte(dados.nova_senha):
        raise HTTPException(status_code=400, detail="Senha fraca. Use letras maiúsculas, minúsculas, número e símbolo.")

    if bcrypt.verify(dados.nova_senha, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="A nova senha não pode ser igual à antiga.")

    usuario.senha_hash = bcrypt.hash(dados.nova_senha)
    db.delete(token)
    db.commit()
    return {"mensagem": "Senha atualizada com sucesso"}
