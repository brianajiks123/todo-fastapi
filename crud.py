from sqlalchemy.orm import Session
from models import Todo, User
from schemas import TodoCreate, TodoUpdate, UserCreate
from utils import get_password_hash

def create_todo(db: Session, todo: TodoCreate):
    db_todo = Todo(**todo.model_dump())

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo

def get_todos(db: Session):
    return db.query(Todo).all()

def get_todo(db: Session, todo_id: int):
    return db.query(Todo).filter(Todo.id == todo_id).first()

def update_todo(db: Session, todo_id: int, todo: TodoUpdate):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if db_todo:
        for key, value in todo.model_dump(exclude_unset=True).items():
            setattr(db_todo, key, value)

        db.commit()
        db.refresh(db_todo)

    return db_todo

def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if db_todo:
        db.delete(db_todo)
        db.commit()

        return True

    return False

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
