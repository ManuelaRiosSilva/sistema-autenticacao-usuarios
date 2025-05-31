import re
from database import SessionLocal
from sqlalchemy.orm import Session
from utils.logs import registrar_log
from datetime import datetime, timedelta
from utils.email import enviar_email_reset, pwd_context, gerar_token
from fastapi import APIRouter, Depends, HTTPException, Request
from models import Usuario, TokenReset, LogAcesso, Papel, UsuarioPapel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import gerar_hash_senha, verificar_senha, criar_token_jwt, verificar_token_jwt
from schemas import UsuarioCreate, TokenJWT, SolicitarResetSenha, TrocarSenha

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def senha_forte(senha: str) -> bool:
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[\W_]", senha):  
        return False
    if re.fullmatch(r"(.)\1{7,}", senha):  
        return False
    return True

@router.post("/cadastro")
def cadastro(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if not senha_forte(usuario.senha):
        raise HTTPException(status_code=400, detail="Senha fraca. Use no mínimo 8 caracteres, com letras maiúsculas, minúsculas, números e símbolos.")
    
    existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        data_criacao=datetime.utcnow(),
        ativo=True,
        anonimizado=False
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    papel_leitor = db.query(Papel).filter(Papel.nome == "leitor").first()
    if not papel_leitor:
        papel_leitor = Papel(nome="leitor")
        db.add(papel_leitor)
        db.commit()
        db.refresh(papel_leitor)

    db.add(UsuarioPapel(usuario_id=novo.id, papel_id=papel_leitor.id))
    db.commit()

    return {"mensagem": "Cadastro realizado com sucesso", "rota": "/frontend/leitor.html"}


@router.delete("/excluir")
def excluir_conta(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == 1).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.ativo = 0
    db.commit()
    return {"mensagem": "Conta desativada com sucesso"}




@router.post("/login", response_model=TokenJWT)
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        registrar_log(db, None, request.client.host, "falha_login")
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    registrar_log(db, usuario.id, request.client.host, "login")
    access_token = criar_token_jwt(usuario.email)
    return {"access_token": access_token}

@router.get("/me")
def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "papeis": [p.papel.nome for p in usuario.papeis]
    }

@router.post("/trocar_senha")
def trocar_senha(payload: TrocarSenha, db: Session = Depends(get_db)):
    token_obj = db.query(TokenReset).filter_by(token=payload.token, em_uso=False).first()
    if not token_obj:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter_by(id=token_obj.usuario_id).first()

    if not senha_forte(payload.nova_senha):
        raise HTTPException(status_code=400, detail="Senha fraca. Use letras maiúsculas, minúsculas, números e símbolos.")

    if verificar_senha(payload.nova_senha, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")

    usuario.senha_hash = gerar_hash_senha(payload.nova_senha)
    token_obj.em_uso = True
    db.commit()

    return {"mensagem": "Senha atualizada com sucesso."}

def somente_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not any(p.papel.nome == 'admin' for p in usuario.papeis):
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario

@router.get("/listar_todos")
def listar_todos(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or "admin" not in [p.papel.nome for p in usuario.papeis]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    usuarios = db.query(Usuario).filter(Usuario.ativo == True).all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "papeis": [p.papel.nome for p in u.papeis]
        })
    return resultado


@router.post("/alterar_papel")
def alterar_papel(dados: dict, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    solicitante = db.query(Usuario).filter(Usuario.email == email).first()

    if not solicitante or "admin" not in [p.papel.nome for p in solicitante.papeis]:
        raise HTTPException(status_code=403, detail="Apenas admins podem alterar papéis.")

    usuario_id = dados["usuario_id"]
    novo_papel_nome = dados["papel"]

    usuario_alvo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    papeis_alvo = [p.papel.nome for p in usuario_alvo.papeis]
    if "admin" in papeis_alvo:
        raise HTTPException(status_code=403, detail="Não é permitido alterar o papel de outro administrador.")

    if novo_papel_nome == "admin":
        raise HTTPException(status_code=403, detail="Admins não podem promover outros usuários a administradores.")

    papel = db.query(Papel).filter(Papel.nome == novo_papel_nome).first()
    if not papel:
        raise HTTPException(status_code=400, detail="Papel inválido.")


    db.query(UsuarioPapel).filter(UsuarioPapel.usuario_id == usuario_id).delete()
    db.add(UsuarioPapel(usuario_id=usuario_id, papel_id=papel.id))

    db.add(LogAcesso(
        usuario_id=solicitante.id,
        acao=f"Alterou papel do usuário {usuario_id} para {novo_papel_nome}",
        data_hora=datetime.utcnow()
    ))

    db.commit()
    return {"mensagem": "Papel atualizado com sucesso"}



@router.get("/rota_por_papel")
def rota_por_papel(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token_jwt(token)
    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()

    if not usuario:
        raise HTTPException(status_code=403, detail="Usuário inativo ou inválido")

    papeis = [p.papel.nome for p in usuario.papeis]
    if "admin" in papeis:
        return {"rota": "/frontend/admin.html"}
    elif "editor" in papeis:
        return {"rota": "/frontend/editor.html"}
    elif "leitor" in papeis:
        return {"rota": "/frontend/leitor.html"}
    else:
        raise HTTPException(status_code=403, detail="Usuário sem papel definido")


@router.post("/esqueci_senha")
def solicitar_reset(dados: SolicitarResetSenha, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(email=dados.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Email não encontrado")

    token = gerar_token()
    expiracao = datetime.utcnow() + timedelta(minutes=30)
    novo_token = TokenReset(token=token, usuario_id=usuario.id, data_expiracao=expiracao, em_uso=False)
    
    db.add(novo_token)
    db.commit()

    link = f"http://127.0.0.1:8000/frontend/reset_senha.html?token={token}"
    enviar_email_reset(usuario.email, link)
    return {"mensagem": "Email de redefinição enviado."}

@router.post("/trocar_senha")
def trocar_senha(payload: TrocarSenha, db: Session = Depends(get_db)):
    token_obj = db.query(TokenReset).filter_by(token=payload.token, em_uso=False).first()
    if not token_obj or token_obj.data_expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter_by(id=token_obj.usuario_id).first()

    if not senha_forte(payload.nova_senha):
        raise HTTPException(status_code=400, detail="Senha fraca. Use letras maiúsculas, minúsculas, números e símbolos.")

    if verificar_senha(payload.nova_senha, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")

    usuario.senha_hash = gerar_hash_senha(payload.nova_senha)  
    token_obj.em_uso = True
    db.commit()

    return {"mensagem": "Senha atualizada com sucesso."}
