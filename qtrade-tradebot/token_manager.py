import requests
import datetime
from models import Token
from utils.env_vars import REFRESH_TOKEN
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, exc
from db import session_manager

# Purpose: define a manager for Tokens (TokenManager) that provide an interface with models
# TODO: use logging instead of print; alert user when expired/error


# class for managing refresh and access tokens; automatically refresh tokens
# interfaces with SQLAlchemy
class TokenManager():
    def __init__(self, sessionmaker: sessionmaker):
        # session will be used to obtain refresh and access tokens
        self.SessionLocal = sessionmaker

        # only used for initialization
        self._check_token()
    
    # will raise an error if None or multiple Tokens found in db
    def _get_token(self, session: Session) -> Token:
        # helper function to avoid detached instance errors: fetch token from database and load into given session
        # token is unique (primary key id = 1)
        token = session.scalars(select(Token).filter(Token.id == 1)).one()

        return token

    # checks if token exists in DB; if a token does not exist, use environment variable to refresh one into db
    def _check_token(self):
        with session_manager(self.SessionLocal) as session:
            # each time a new token is refreshed token will be stored on id of 1: overwritten for each new refresh
            
            # thus only one token should be in the database
            try:
                result = self._get_token(session)
            except exc.NoResultFound:
                # exception will occur if no token was in db
                # no token in database: grab from environment variable (likely expired)
                # will need to check for expiry separately
                from utils.env_vars import REFRESH_TOKEN

                # refresh_tokens to get new pair; refresh_tokens will set self.token
                self._refresh_tokens(session, rf_token = REFRESH_TOKEN)
            except:
                raise
                

    # will overwrite existing token row or add row if none exist
    # does not check for expiry logic!
    def _refresh_tokens(self, session: Session, rf_token = None):
        # session can be passed to refresh_tokens to ensure that transactions completed in refresh_tokens remain consistent with parent function

        REFRESH_ADDRESS = 'https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={token}'

        token_to_use = rf_token or self.refresh_token
        # use property to access refresh_token in case none are given

        # query for new refresh + access token
        result = requests.get(REFRESH_ADDRESS.format(token = token_to_use))
            
        try:
            result.raise_for_status()

        except requests.HTTPError:
            print(f"Error Occurred! Status Code: {result.status_code}")
            raise requests.HTTPError
            # implement logic to notify user via SMS/Email later


        parsed_token = self._parse_result(result)
        # parse_result returns a Token object to be commited to session

        session.merge(parsed_token)
        # session_manager will automatically commit

    
    @property
    def access_token(self):
        # every retrieval of the token should check for expiry 

        with session_manager(self.SessionLocal) as session:
            token = self._get_token(session)

            # check for expiry
            if datetime.datetime.now() >= token.expiry_date:
                # access token is expired: attempt to refresh
                print("Attempting refresh: access token was expired on: ", token.expiry_date) # for testing purposes
                
                self._refresh_tokens(session)

                session.refresh()
                
                
        
            return token.access_token 
    

    @property
    def refresh_token(self):
        with session_manager(self.SessionLocal) as session:
            # not going to check refresh token expiry: access_token is the limiting factor
            token = self._get_token(session)
            return token.refresh_token


    def _parse_result(self, result) -> Token:
        json_results = result.json()
        
        # print results for troubleshooting
        print(json_results)


        token = Token(
            id = 1, # primary key: always 1 
            access_token = json_results['access_token'], 
            refresh_token = json_results['refresh_token'], 
            api_server = json_results['api_server'], 
            expiry_date = datetime.datetime.now() + datetime.timedelta(seconds = json_results['expires_in'])
        )
        
        return token

'''
    def check_expiry(self):
        # must only be called within sessions where self.token is accessible (not detached)
        if self.token is None:
            raise RuntimeError("Error: token is not yet defined")
        
        print(self.token.expiry_date) # for testing purposes
        return datetime.datetime.now() >= self.token.expiry_date
'''