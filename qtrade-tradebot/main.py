from token_manager import TokenManager
from db import session_maker
import atexit
    
# testing
token = TokenManager(session_maker)

print(f'refresh token: {token.refresh_token}')
print(f'access token: {token.access_token}')

@atexit.register
def exit_msg():
    #TODO: email user that bot as quit unexpectedly/from error
    print("Program exited!")