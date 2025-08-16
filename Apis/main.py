# mi primer api
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return{"message": "hello world"}

@app.get("/saludo/{nombre}")

def get_saludo(nombre: str):
    return{"message": f"Hola, {nombre}!"}

participante = []

@app.post("/participante")
def create_participante(nombre: str) -> dict[str,str]:
    nuevo = {"id" : len(participante)+1, "nombre":nombre}
    participante.append(nuevo)
    return nuevo