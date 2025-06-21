import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("postgresql://mydatabase_8ulu_user:gO1Rsd1SPznjAUf2tYGoHdTrNxONKIxj@dpg-d1bbqqeuk2gs739jkmag-a/mydatabase_8ulu", "sqlite:///./people.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
