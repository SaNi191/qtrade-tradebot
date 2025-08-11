from token_manager import TokenManager
from db import session_maker

    
# testing
token = TokenManager(session_maker)

print(f'refresh token: {token.refresh_token}')
print(f'access token: {token.access_token}')

