import asyncio
from api import QTradeAPI

async def schedule_checks(api_helper: QTradeAPI, delay: int = 300):
    # default 5 minute delay between updates
    while True:
        await asyncio.to_thread(api_helper.get_all_stocks)
        await asyncio.sleep(delay)


async def schedule_alert(api_helper: QTradeAPI, delay: int = 86400):
    # default once per day notification
    while True:
        await asyncio.to_thread(api_helper.stocks.alert_stocks)
        await asyncio.sleep(delay)

'''
TODO:
usage of to_thread can be avoided by reworking db and network operations 
using async-friendly packages/extensions
'''



