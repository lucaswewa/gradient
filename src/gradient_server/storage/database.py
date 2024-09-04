from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/sql_app.db"
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username="postgres",
    password="password",
    host="localhost",
    database="test",
)

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
