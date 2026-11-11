
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Locate the .env file in the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from the .env file.")

# Create the SQLAlchemy database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Test the database connection
def check_database_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        return True
