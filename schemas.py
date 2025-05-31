from datetime import datetime
from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    data_criacao: datetime
    ativo: bool
    class Config:
        from_attributes = True

class LoginInput(BaseModel):
    email: EmailStr
    senha: str

class ResetSenhaInput(BaseModel):
    email: EmailStr

class NovaSenhaInput(BaseModel):
    token: str
    nova_senha: str

class TokenJWT(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class SolicitarResetSenha(BaseModel):
    email: EmailStr

class TrocarSenha(BaseModel):
    nova_senha: str
    token: str

