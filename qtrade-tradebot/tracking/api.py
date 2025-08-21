import requests
import asyncio
import logging
from websockets.exceptions import ConnectionClosed

from websockets.asyncio.client import connect

from token_manager import TokenManager
from tracking.stock_tracker import StockTracker
from sqlalchemy.orm import sessionmaker

# implementation of QTradeWorker
# - utilizes both StockTracker and TokenManager
# - adds async functionality and websocket connection to the QuestTrade API



class QTradeWorker():
    def __init__(self, sessionmaker: sessionmaker) -> None:
        self.token = TokenManager(sessionmaker)
        self.stocks = StockTracker(sessionmaker)
        self.running = False
        self.latest_changes = {}

    async def async_get_access_token(self):
        # since token.access_token is a property, use lambda to turn to func
        return await asyncio.to_thread(lambda: self.token.access_token)
    
    async def get_websocket_listener(self):

        while self.running:
            try:
                async with connect(uri = "") as ws:
                    pass
            except ConnectionClosed:
                pass

    async def update_stock_data(self):
        for change_key in self.latest_changes:
            changes = self.latest_changes[change_key]
            self.stocks.



    async def _start(self):
        self.running = True
        asyncio.create_task(self.get_websocket_listener)
        asyncio.create_task()

    async def _stop(self):
        self.running = False

    


    
