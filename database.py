from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}) # allow one thread to access the database at a time
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # create a session factory that will create new sessions for each request

Base = declarative_base() # create a base class for our models to inherit from