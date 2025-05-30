from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "segredo_super_secreto_para_jwt"
ALGORITHM = "HS256"
TOKEN_EXPIRA_MIN = 30

def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)

def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def criar_token_jwt(email: str):
    expiracao = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRA_MIN)
    to_encode = {"sub": email, "exp": expiracao}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
