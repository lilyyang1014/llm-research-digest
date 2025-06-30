from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config  # Import the refactored Config class

# --- 1. Create the Database Engine ---
# create_engine establishes a connection to the database based on the DATABASE_URL.
# The `connect_args` dictionary is a special configuration required for SQLite.
# It allows multiple threads to share the same connection, which is necessary
# for FastAPI's asynchronous nature. This argument is not needed for PostgreSQL.
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)

# --- 2. Create a Session Factory ---
# sessionmaker creates a SessionLocal class. Instances of this class will be the
# actual database sessions. You can think of it as a "session template".
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 3. Create a Declarative Base ---
# Base is a class that our ORM models will inherit from.
# SQLAlchemy uses this base class to keep track of all the mapped models
# and associate them with their corresponding database tables.
Base = declarative_base()

# --- 4. Create a Database Session Dependency ---
# This is a crucial function that will be used as a dependency in your API endpoints.
# It ensures that each request gets an independent database session and that
# the session is always closed after the request is finished.
def get_db():
    """
    A dependency function for FastAPI to get a database session.
    It ensures the database session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()