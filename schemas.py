from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class TokenJWT(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class SolicitarResetSenha(BaseModel):
    email: EmailStr

class TrocarSenha(BaseModel):
    nova_senha: str
    token: str

