from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Books
from auth import router, get_current_user

app = FastAPI()
app.include_router(router)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class BookCreate(BaseModel):
    id: int
    title: str = Field(min_length=4)
    author: str
    description: str = Field(min_length=10, max_length=70)
    year_published: int
    language: str


@app.get("/")
async def welcome():
    return {"message": "Welcome to the book API!"}


@app.get("/books")
async def get_books(db: db_dependency, user: user_dependency):
    return db.query(Books).all()


@app.post("/create_book")
async def create_book(book: BookCreate, db: db_dependency, user: user_dependency):
    new_book = Books(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.put("/update_book/{book_id}")
async def update_book(
    book_id: int,
    book: BookCreate,
    db: db_dependency,
    user: user_dependency
):
    db_book = db.query(Books).filter(Books.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.model_dump().items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)

    return db_book


@app.delete("/delete_book/{book_id}")
async def delete_book(
    book_id: int,
    db: db_dependency,
    user: user_dependency
):
    book = db.query(Books).filter(Books.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}