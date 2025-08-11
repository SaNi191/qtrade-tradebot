### TODO: move engine, session, db initialization to separate module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


# creating SQLAlchemy engine and session connecting to bot.db
engine = create_engine('sqlite:///bot.db', echo = True)

session_maker = sessionmaker(bind = engine, expire_on_commit=False)

Base.metadata.create_all(engine)




    
    