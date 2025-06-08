from token_manager import TokenManager
from db import session
    
# testing
token = TokenManager(session)
print(f'refresh token: {token.refresh_token}')
print(f'access token: {token.access_token}')


