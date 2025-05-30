from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import usuarios, logs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])

@app.get("/")
def raiz():
    return {"mensagem": "API de autenticação pronta"}
