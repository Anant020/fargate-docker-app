from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel , Field
import auth
from typing import Annotated
app = FastAPI()
app.include_router(auth.router)
from auth import get_current_user
user_dependency = Annotated[dict, Depends(get_current_user)]
class Book:
    id: int
    title: str
    author: str
    description: str
    year_published: int
    language: str

    def __init__ (self, id , title, author, description, year_published, language):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.year_published = year_published
        self.language = language

class BookCreate(BaseModel):
    id: int
    title: str = Field(min_length=4)
    author: str
    description: str = Field(min_length=10, max_length=70)
    year_published: int
    language: str

books = [
    Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "A novel about the American dream", 1925, "English"),
    Book(2, "To Kill a Mockingbird", "Harper Lee", "A novel about racial injustice in the Deep South", 1960, "English"),
    Book(3, "Board a Broken ship", "Geiong tarp", "A novel about a broken ship and the adventures of its crew", 2000, "English"),
    Book(4, "Be your best self", "Alex torn", "A self-help book about personal development and achieving your goals", 2010, "English"),
    Book(5, "1984", "George Orwell", "A dystopian novel about a totalitarian society ruled by Big Brother", 1948, "Spanish"),
    Book(6, "Friends", "Martha Kauffman", "A novel about a group of friends living in New York City and their relationships with each other", 1994, "English")
]

@app.get("/")
async def welcome():
    return {"message": "Welcome to the book API!"}

@app.get("/books")
async def get_books(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return books

@app.post("/create_book")
async def create_books(book: BookCreate, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_book = Book(**book.model_dump())
    books.append(new_book)

@app.put("/update_book/{book_id}")
async def update_book(book_id: int, book: BookCreate, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    for x in books:
        if x.id == book_id:
            updated_book = Book(**book.model_dump())
            books[books.index(x)] = updated_book
            return updated_book
    return {"message": "Book not found"}

@app.delete("/delete_book/{book_id}")
async def delete_book(book_id: int, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    for x in books:
        if x.id == book_id:
            books.remove(x)
            return {"message": "Book deleted successfully"}
    return {"message": "Book not found"}

@app.put("/book_put/{book_id}")
async def put_book(book_id : int, book : BookCreate, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    for i in books:
        if i.id == book_id:
            updated_book = Book(**book.model_dump())
            books[books.index(i)] = updated_book
            return updated_book
    return {"message": "Book not found"}




