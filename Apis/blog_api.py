from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(
    title="Blog API",
    description="Una API realista para gestión de posts y usuarios",
    version="1.0.0"
)

# Modelos de datos usando Pydantic
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: str = Field(..., description="Email del usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class User(UserBase):
    id: str
    created_at: datetime
    is_active: bool = True

class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, description="Título del post")
    content: str = Field(..., min_length=10, description="Contenido del post")
    tags: List[str] = Field(default=[], description="Tags del post")

class PostCreate(PostBase):
    author_id: str = Field(..., description="ID del autor del post")

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None

class Post(PostBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    likes: int = 0
    views: int = 0

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500, description="Contenido del comentario")

class CommentCreate(CommentBase):
    post_id: str = Field(..., description="ID del post")
    author_id: str = Field(..., description="ID del autor del comentario")

class Comment(CommentBase):
    id: str
    post_id: str
    author_id: str
    created_at: datetime

# Base de datos simulada
users_db = {}
posts_db = {}
comments_db = {}

# Endpoints para usuarios
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Crear un nuevo usuario"""
    # Verificar si el username ya existe
    if any(u["username"] == user.username for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe"
        )
    
    # Verificar si el email ya existe
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    user_id = str(uuid.uuid4())
    user_data = User(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=datetime.now(),
        password=user.password 
    )
    
    users_db[user_id] = user_data.dict()
    return user_data

@app.get("/users", response_model=List[User])
def get_users(skip: int = 0, limit: int = 10):
    """Obtener lista de usuarios con paginación"""
    users = list(users_db.values())[skip: skip + limit]
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    """Obtener un usuario específico por ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return users_db[user_id]

@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    """Crear un nuevo post"""
    if post.author_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )
    
    post_id = str(uuid.uuid4())
    now = datetime.now()
    post_data = Post(
        id=post_id,
        title=post.title,
        content=post.content,
        tags=post.tags,
        author_id=post.author_id,
        created_at=now,
        updated_at=now
    )
    
    posts_db[post_id] = post_data.dict()
    return post_data

@app.get("/posts", response_model=List[Post])
def get_posts(
    skip: int = 0, 
    limit: int = 10,
    tag: Optional[str] = None,
    author_id: Optional[str] = None
):
    """Obtener posts con filtros y paginación"""
    posts = list(posts_db.values())
    
    if tag:
        posts = [p for p in posts if tag in p["tags"]]
    
    if author_id:
        posts = [p for p in posts if p["author_id"] == author_id]
    
    return posts[skip: skip + limit]

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    """Obtener un post específico por ID"""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    posts_db[post_id]["views"] += 1
    return posts_db[post_id]

@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: str, post_update: PostUpdate):
    """Actualizar un post existente"""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    post = posts_db[post_id]
    
    if post_update.title is not None:
        post["title"] = post_update.title
    if post_update.content is not None:
        post["content"] = post_update.content
    if post_update.tags is not None:
        post["tags"] = post_update.tags
    
    post["updated_at"] = datetime.now()
    return post

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str):
    """Eliminar un post"""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    del posts_db[post_id]
    
    comments_to_delete = [c_id for c_id, comment in comments_db.items() 
                         if comment["post_id"] == post_id]
    for c_id in comments_to_delete:
        del comments_db[c_id]

@app.post("/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate):
    """Crear un nuevo comentario"""
    if comment.post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    if comment.author_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )
    
    comment_id = str(uuid.uuid4())
    comment_data = Comment(
        id=comment_id,
        content=comment.content,
        post_id=comment.post_id,
        author_id=comment.author_id,
        created_at=datetime.now()
    )
    
    comments_db[comment_id] = comment_data.dict()
    return comment_data

@app.get("/posts/{post_id}/comments", response_model=List[Comment])
def get_post_comments(post_id: str, skip: int = 0, limit: int = 10):
    """Obtener comentarios de un post específico"""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    post_comments = [c for c in comments_db.values() if c["post_id"] == post_id]
    return post_comments[skip: skip + limit]

@app.post("/posts/{post_id}/like", response_model=Post)
def like_post(post_id: str):
    """Dar like a un post"""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post no encontrado"
        )
    
    posts_db[post_id]["likes"] += 1
    return posts_db[post_id]

@app.get("/search", response_model=List[Post])
def search_posts(q: str, skip: int = 0, limit: int = 10):
    """Buscar posts por título o contenido"""
    posts = []
    query = q.lower()
    
    for post in posts_db.values():
        if (query in post["title"].lower() or 
            query in post["content"].lower() or
            any(query in tag.lower() for tag in post["tags"])):
            posts.append(post)
    
    return posts[skip: skip + limit]

@app.get("/stats")
def get_stats():
    """Obtener estadísticas generales de la API"""
    total_users = len(users_db)
    total_posts = len(posts_db)
    total_comments = len(comments_db)
    total_likes = sum(post["likes"] for post in posts_db.values())
    total_views = sum(post["views"] for post in posts_db.values())
    
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_likes": total_likes,
        "total_views": total_views,
        "average_likes_per_post": total_likes / total_posts if total_posts > 0 else 0,
        "average_views_per_post": total_views / total_posts if total_posts > 0 else 0
    }

@app.get("/")
def read_root():
    return {
        "message": "¡Bienvenido a la Blog API!",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "posts": "/posts", 
            "comments": "/comments",
            "search": "/search",
            "stats": "/stats",
            "docs": "/docs"
        }
    }