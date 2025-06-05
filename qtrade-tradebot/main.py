from env_vars import REFRESH_TOKEN
import datetime
from models import Tokens, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import requests

### TODO: move engine, session, db initialization to seperate module

# creating SQLAlchemy engine and session connecting to bot.db
engine = create_engine('sqlite:///bot.db', echo = True)

session_maker = sessionmaker(bind = engine)

session = session_maker()

Base.metadata.create_all(engine)



# main class for managing refresh and access tokens; automatically refresh OAuth tokens
class TokenManager():
    def __init__(self, session: Session):
        # session will be used to obtain refresh and access tokens
        self.session = session

        # only run at the beginning, contains starting token logic
        self.get_token()
    

    def get_token(self):
        with self.session as session:
            # each time a new token is refreshed, replace obsolete old data
            # thus only one token should be in the database
            # token will be stored on id of 1: overwritten for each new refresh
            result = session.query(Tokens).filter(Tokens.id == 1).first()
            # returns either None or Tokens object
            
            if result is None:
                # no token in database: grab from environment variable (likely expired)
                # will need to check for expiry separately

                from env_vars import REFRESH_TOKEN

                # do not add this bootstrap token to db, refresh_tokens to get new pair
                self.refresh_tokens(refresh_token = REFRESH_TOKEN)
            
                
            else:
                self.token = result

    # will overwrite existing token row or add row if none exist
    # does not check for expiry logic!
    def refresh_tokens(self, **kwargs):
        ADDRESS = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={token}'

        if 'refresh_token' in kwargs:
            # if given a starter refresh_token (from environment variable) use it
            result = requests.get(ADDRESS.format(kwargs['refresh_token']))

        else:
            # otherwise, assume that self.token is set and utilize self.token to get 
            result = requests.get(ADDRESS.format(self.token.refresh_token))

        try:
            result.raise_for_status()
            
        except requests.HTTPError:
            print(f"Error Occurred! Status Code: {result.status_code}")
            raise requests.HTTPError
            # implement logic to notify user via SMS/Email later

        # status is 200:
        parsed_results = self.parse_result(result)
        # parse_result will return a Token object to be commited to session


        with self.session as session:
            session.add(parsed_results)
            session.commit()
        


    def parse_result(self, result) -> Tokens:
        json_results = result.json()
        
        token = Tokens(
            access_token = json_results['access_token'], 
            refresh_token = json_results['refresh_token'], 
            api_server = json_results['api_server'], 
            expiry_date = json_results['expiry_date']
            )
        
        return token




