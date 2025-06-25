import models, logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List
from sqlalchemy.orm import Session
from schemas import Todo, TodoCreate, TodoUpdate, User, UserCreate
from database import get_db, init_db
from crud import create_todo, get_todos, get_todo, update_todo, delete_todo, create_user, get_user_by_username
from auth import get_current_user, create_access_token, Token
from utils import verify_password

# Setup Logging
logging.basicConfig(level = logging.INFO)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Initialize database
    logger.info(f"Starting application: {app.title}")
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown: Log application shutdown
    logger.info(f"Shutting down application: {app.title}")

app = FastAPI(title = "Todo API", lifespan = lifespan)

@app.post("/register", response_model = User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username = user.username)

    if db_user:
        raise HTTPException(status_code = 400, detail = "Username already registered")

    return create_user(db, user)

@app.post("/login", response_model = Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username = form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data = {"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/", response_model = Todo)
def create_todo_endpoint(todo: TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} creating a new todo")

    return create_todo(db, todo)

@app.get("/todos/", response_model = List[Todo])
def get_todos_endpoint(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} retrieving all todos")

    return get_todos(db)

@app.get("/todos/{todo_id}", response_model = Todo)
def get_todo_endpoint(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} retrieving todo with id {todo_id}")

    todo = get_todo(db, todo_id)

    if not todo:
        raise HTTPException(status_code = 404, detail = "Todo not found")

    return todo

@app.put("/todos/{todo_id}", response_model = Todo)
def update_todo_endpoint(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} updating todo with id {todo_id}")

    updated_todo = update_todo(db, todo_id, todo)

    if not updated_todo:
        raise HTTPException(status_code = 404, detail = "Todo not found")

    return updated_todo

@app.delete("/todos/{todo_id}")
def delete_todo_endpoint(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} deleting todo with id {todo_id}")

    if not delete_todo(db, todo_id):
        raise HTTPException(status_code = 404, detail = "Todo not found")

    return {"message": "Todo deleted successfully"}
