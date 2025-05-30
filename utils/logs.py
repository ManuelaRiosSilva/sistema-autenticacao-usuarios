from models import LogAcesso
from datetime import datetime

def registrar_log(db, usuario_id, ip, acao):
    log = LogAcesso(usuario_id=usuario_id, ip=ip, acao=acao, data_hora=datetime.utcnow())
    db.add(log)
    db.commit()
