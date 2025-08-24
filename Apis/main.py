from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="Api de ejemplo para documentación",
              description="Ejemplo de un API con autpodocumentacion y documentacion swagger",
              version="1.0.0")

class User(BaseModel):
    id: int = Field(..., examples=[1])
    name: str = Field(..., examples=["Alejandro Salgar"])
    email: str = Field(..., examples=["alejandro.salgar@gmail.com"])


user_db: List[User] = []

@app.get(
    "/users",
    response_model=List[User],
    summary="Obtener todos los usuarios",
    description="Esto nos devuelve una lista con todos los usuarios registrados",
    tags=["Usuarios"],
    responses={
        200: {
            "descripcion": "Lista de usuarios recuperada exitosamente."
        }
    }
)
def get_users() -> List[User]:
    return user_db

@app.post(
    "/users",
    status_code=201,
    summary="Crear un usuario",
    description="Agerga un nuevo usuario a la base de datos simulada",
    tags=["Usuarios"],
    responses={
        201: {
            "descripcion":"usuaario creado exitosamente"
        },
        400: {
            "descripcion": "id duplicado"
        }
    }
)
def crear_user(user: User) -> User:
    for cada_usuario in user_db:
        if cada_usuario.id == user.id:
            raise HTTPException(status_code=400,detail="El ID ya existe")
    user_db.append(user)
    return user

@app.put(
    "/users/{user_id}",
    response_model= User,
    summary="Actualizar un usario",
    description="Se actualiza el usuario mediante su ID",
    tags=["Usuarios"],
    responses={
        200: {"descripcion": "usuario actualizado correctamente"},
        404:{"descripcion": "id usuario no se encontro"}
    }
)
def actualizar_usuario(user_id: int, update_user: User):
    for index, usuario_existente in enumerate(user_db):
        if usuario_existente.id == user_id:
            user_db[index] = update_user
            return update_user
    raise HTTPException(status_code=404,detail="Usuario no encontrado")

# @app.delete(
#     "/users/{user_id}",
#     summary="Eliminar un usuario",
#     description="Se elimina un usuario de la base de datos por Id",
#     tags=["Usuarios"],
#     responses={
#         200: {"descripcion": "usuario eliminado correctamente"},
#         404:{"descripcion": "id usuario no se encontro"}
#     }
# )