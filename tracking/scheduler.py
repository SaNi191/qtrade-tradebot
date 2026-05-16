import asyncio
import logging

from .api import QTradeAPI

logger = logging.getLogger(__name__)

async def schedule_checks(api_helper: QTradeAPI, delay: int = 300):
    # default 5 minute delay between updates
    while True:
        try:
            await asyncio.to_thread(api_helper.get_all_stocks)
        except Exception:
            logger.exception("Scheduled stock check failed.")
        await asyncio.sleep(delay)


async def schedule_alert(api_helper: QTradeAPI, delay: int = 86400):
    # default once per day notification
    while True:
        try:
            await asyncio.to_thread(api_helper.stocks.alert_stocks)
        except Exception:
            logger.exception("Scheduled alert dispatch failed.")
        await asyncio.sleep(delay)

'''
TODO:
usage of to_thread can be avoided by reworking db and network operations 
using async-friendly packages/extensions
'''


