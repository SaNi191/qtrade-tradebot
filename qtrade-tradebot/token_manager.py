import requests
import datetime
from models import Tokens
from env_vars import REFRESH_TOKEN
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select
from contextlib import contextmanager

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


# main class for managing refresh and access tokens; automatically refresh OAuth tokens
# interfaces with SQLAlchemy
class TokenManager():
    def __init__(self, sessionmaker: sessionmaker):
        # session will be used to obtain refresh and access tokens
        self.SessionLocal = sessionmaker

        # only used for initialization
        self.check_token()
    
    def get_token(self, session: Session):
        # helper function to avoid detached instance errors: fetch token from database and load into given session
        # token is unique (primary key id = 1)
        pass


    # checks if token exists in DB; if a token does not exist, use environment variable
    def check_token(self):
        with session_manager(self.SessionLocal) as session:
            # each time a new token is refreshed token will be stored on id of 1: overwritten for each new refresh
            
            # thus only one token should be in the database
            result = session.scalars(select(Tokens).filter(Tokens.id == 1)).first()
            # returns either None or a Tokens object
            # use first() in case no token is in db. in future queries use one() to enforce uniqueness
            
            if result is None:
                # no token in database: grab from environment variable (likely expired)
                # will need to check for expiry separately
                from env_vars import REFRESH_TOKEN

                # refresh_tokens to get new pair; refresh_tokens will set self.token
                self.refresh_tokens(session, refresh_token = REFRESH_TOKEN)

                
            else:
                self.token = result
                # note: will become detached when session closes!
                # will need to be reattached with session.merge when accessed in the future


    # will overwrite existing token row or add row if none exist
    # does not check for expiry logic!
    def refresh_tokens(self, session: Session, refresh_token = None):
        # session can be passed to refresh_tokens to ensure that transactions completed in refresh_tokens remain consistent with parent function


        REFRESH_ADDRESS = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={token}'

        token_to_use = refresh_token or session.scalars(select(Tokens).filter(Tokens.id == 1)).one()

        # query for new refresh + access token
        result = requests.get(REFRESH_ADDRESS.format(token = token_to_use))
            
        try:
            result.raise_for_status()

        except requests.HTTPError:
            print(f"Error Occurred! Status Code: {result.status_code}")
            raise requests.HTTPError
            # implement logic to notify user via SMS/Email later


        parsed_token = self.parse_result(result)
        # parse_result returns a Tokens object to be commited to session

        session.merge(parsed_token)
        session.commit()
        
        self.token = parsed_token
    

    def parse_result(self, result) -> Tokens:
        json_results = result.json()
        
        # print results for troubleshooting
        print(json_results)


        token = Tokens(
            id = 1, # primary key: always 1 
            access_token = json_results['access_token'], 
            refresh_token = json_results['refresh_token'], 
            api_server = json_results['api_server'], 
            expiry_date = datetime.datetime.now() + datetime.timedelta(seconds = json_results['expires_in'])
        )
        
        return token

    @property
    def access_token(self):
        # every retrieval of the token should check for expiry 

        with session_manager(self.SessionLocal) as session:
            if self.token is None:
                raise RuntimeError("Error: token is not defined!")
            
            self.token = session.merge(self.token)
            if self.check_expiry():
                print("Error: access token is expired!")

                # refresh the token
                self.refresh_tokens(session)
                    
        
            return self.token.access_token 
    

    @property
    def refresh_token(self):
        with session_manager(self.SessionLocal) as session:
            if self.token is None:
                raise RuntimeError("Error: token is not yet defined!")
            # not going to check refresh token expiry: access_token is the limiting factor

            self.token = session.merge(self.token)
            return self.token.refresh_token 

    def check_expiry(self):
        # must only be called within sessions where self.token is accessible (not detached)
        if self.token is None:
            raise RuntimeError("Error: token is not yet defined")
        
        print(self.token.expiry_date) # for testing purposes
        return datetime.datetime.now() >= self.token.expiry_date
