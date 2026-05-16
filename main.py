import atexit
import asyncio
import logging

from database.db import session_maker, init_db
from tracking.api import QTradeAPI
from tracking.scheduler import schedule_alert, schedule_checks
from utils.env_vars import get_settings

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

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
    try:
        get_settings().validate_startup()
        init_db()
        asyncio.run(main())
    except RuntimeError as exc:
        logger.error(f"Startup failed: {exc}")
        raise SystemExit(1) from exc
