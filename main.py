from fastapi import FastAPI
from routes import usuarios, logs
from database import Base, engine
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(usuarios.router, tags=["Usuários"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])

@app.get("/")
def raiz():
    return {"mensagem": "API de autenticação pronta"}
