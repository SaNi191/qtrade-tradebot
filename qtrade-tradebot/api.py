from token_manager import TokenManager
from sqlalchemy.orm import sessionmaker

# implementation of QTradeAPI 
# - interface for accessing questtrade API endpoints
# - utilize TokenManager for OAuth



class QTradeAPI:
    def __init__(self, sessionmaker: sessionmaker) -> None:
        self.token = TokenManager(sessionmaker)



    
