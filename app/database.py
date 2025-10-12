from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This should match our alembic.ini file
DATABASE_URL = "postgresql://postgres:thisisme2010@localhost/first-db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
This file sets up the connection to the PostgreSQL database and creates
a session-making utility that the rest of the application uses to talk to
the database.
"""
