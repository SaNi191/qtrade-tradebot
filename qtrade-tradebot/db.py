### TODO: move engine, session, db initialization to separate module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session
from models import Base
from contextlib import contextmanager


# creating SQLAlchemy engine and session connecting to bot.db
engine = create_engine('sqlite:///bot.db', echo = True)
session_maker = sessionmaker(bind = engine, expire_on_commit=False)

@contextmanager
def session_manager(SessionLocal: sessionmaker):
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(f"Exception Occurred {e}")
        session.rollback()
        raise e
    finally:
        session.close()

def init_db():
    Base.metadata.create_all(engine)


    
    