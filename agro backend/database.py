from sqlmodel import SQLModel, create_engine, Session
# Import our models so the database knows what tables to create
import models 

sqlite_file_name = "agro_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session