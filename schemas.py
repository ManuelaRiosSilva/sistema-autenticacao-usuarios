from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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
