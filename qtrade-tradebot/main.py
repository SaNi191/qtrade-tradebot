from token_manager import TokenManager
from db import session_maker
import atexit
import logging
logger = logging.getLogger(__name__)

@atexit.register
def exit_msg():
    #TODO: email user that bot as quit unexpectedly/from error
    logger.info("Program exited!")

# testing
token = TokenManager(session_maker)

logger.info(f'refresh token: {token.get_refresh_token()}')
logger.info(f'access token: {token.get_access_token()}')

