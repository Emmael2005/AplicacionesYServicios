# mi primer api
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return{"message": "hello world"}

@app.get("/saludo/{nombre}")

def get_saludo(nombre: str):
    return{"message": f"Hola, {nombre}!"}

participantes = []

@app.get("/participantes")
def listar_participantes() -> list[dict[str,str]]:
    return participantes