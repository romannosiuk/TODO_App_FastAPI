import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
if not SQLALCHEMY_DATABASE_URI:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI is not set (add it to .env or the host's environment)")

# Some hosted providers hand out "postgres://", which SQLAlchemy 2 does not accept
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

# pool_pre_ping drops connections that a remote database closed while idle
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

