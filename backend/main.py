from fastapi import FastAPI

app = FastAPI (

    title = "Sistema de Controle de Acesso",
    description = "API de reconhecimento de placas e controle de acesso.",
    version = "1.0.0"
)

@app.get ("/")

def home():

    return {
        "mensagem": "Sistema de Controle de Acesso - API de reconhecimento de placas e controle de acesso.",
        "status": "API está funcionando corretamente."
    }