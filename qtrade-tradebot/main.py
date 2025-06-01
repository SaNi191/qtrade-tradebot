from env_vars import ACCESS_TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# creating SQLAlchemy engine and session connecting to bot.db
engine = create_engine('sqlite:///bot.db', echo = True)

session = sessionmaker(bind = engine)

from models import Base, Tokens
Base.metadata.create_all(engine)



class TokenManager():
    def __init__(self, session):
        # session will be used to obtain refresh and access tokens
        self.session = session
        self.get_refresh_token()
        self.get_access_token()
    
    def get_refresh_token(self):
        with self.session() as session:
            result = session.select(Tokens).where(Tokens.id == 1)
            if result is None:
                # no refresh token in database: grab from environment variable (likely expired)
                # will need to check for expiry 
                from env_vars import BOT_TOKEN
                base_token = Tokens()



    def get_access_token(self):
        pass



print(ACCESS_TOKEN)

