import atexit
import asyncio
import logging

from database.token_manager import TokenManager
from database.db import session_maker
from tracking.api import QTradeAPI
from tracking.scheduler import schedule_alert, schedule_checks


logger = logging.getLogger(__name__)

@atexit.register
def exit_msg():
    #TODO: notify user that bot as quit
    logger.info("Program exited!")

async def main():
    api = QTradeAPI(sessionmaker = session_maker)
    check_task = asyncio.create_task(schedule_checks(api))
    alert_task = asyncio.create_task(schedule_alert(api))

    await asyncio.gather(check_task, alert_task)

if __name__ == "__main__":
    asyncio.run(main())



# testing

token = TokenManager(session_maker)

logger.info(f'refresh token: {token.get_refresh_token()}')
logger.info(f'access token: {token.get_access_token()}')

