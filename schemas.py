from pydantic import BaseModel, EmailStr, field_validator
import re


class UsuarioBase(BaseModel):
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    nome: str
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'\d', v):
            raise ValueError("A senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")
        return v


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class EsqueciSenhaRequest(BaseModel):
    email: EmailStr

class NovaSenhaRequest(BaseModel):
    token: str
    nova_senha: str


class UsuarioResetSenha(BaseModel):
    email: EmailStr


class UsuarioNovaSenha(BaseModel):
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_nova_senha(cls, v):
        if len(v) < 8:
            raise ValueError("A nova senha deve ter no mínimo 8 caracteres.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("A nova senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', v):
            raise ValueError("A nova senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'\d', v):
            raise ValueError("A nova senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', v):
            raise ValueError("A nova senha deve conter pelo menos um caractere especial.")
        return v
