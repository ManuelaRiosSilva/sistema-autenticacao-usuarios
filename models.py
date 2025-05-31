from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    senha_hash = Column(String(250))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_exclusao = Column(DateTime, nullable=True)
    ativo = Column(Boolean, default=True)
    anonimizado = Column(Boolean, default=False)
    tokens_reset = relationship("TokenReset", back_populates="usuario")

    papeis = relationship("UsuarioPapel", back_populates="usuario")
    logs = relationship("LogAcesso", back_populates="usuario")

class Papel(Base):
    __tablename__ = "papeis"
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True)

class UsuarioPapel(Base):
    __tablename__ = "usuario_papel"
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    papel_id = Column(Integer, ForeignKey("papeis.id"), primary_key=True)
    usuario = relationship("Usuario", back_populates="papeis")
    papel = relationship("Papel")

class TokenReset(Base):
    __tablename__ = "tokens_reset"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    criado_em = Column(DateTime, default=datetime.utcnow)
    expirado = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="tokens_reset")

class LogAcesso(Base):
    __tablename__ = "logs_acesso"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    ip = Column(String(45))
    acao = Column(String(50))
    data_hora = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="logs")
