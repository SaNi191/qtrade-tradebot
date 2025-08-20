import requests

from token_manager import TokenManager
from sqlalchemy.orm import sessionmaker

# implementation of QTradeAPI 
# - interface for accessing questtrade API endpoints
# - utilize TokenManager for OAuth



class QTradeWorker():
    def __init__(self, sessionmaker: sessionmaker) -> None:
        self.token = TokenManager(sessionmaker)

    @property
    def header(self):
        # return a header for GET requests
        header = {
            'Authorization': f'Bearer {self.token.access_token}'
        }
        return header
    
    def get_stock(self, stock: str):
        pass


    
