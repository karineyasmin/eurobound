import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://geouser:geopassword@localhost:5432/eurobound_spatial_db"
)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit = False, autoflush=False, bind=engine
)

Base = declarative_base()

def get_db_session():
    """
    Dependency generator to yield database sessions.
    Ensures the connection is always closed properly after the request lifecycle.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()