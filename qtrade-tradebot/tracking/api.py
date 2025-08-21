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
        self._running = False


        self._change_lock = asyncio.Lock()
        self._latest_changes = {}

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
        while self.running:
            # process changes and save in shallow copy to free resource
            async with self._change_lock:
                latest_changes = self._latest_changes.copy()
                self._latest_changes.clear()

            for change_key, changed_price in latest_changes.items():
                await asyncio.to_thread(self.stocks.check_stock, change_key, changed_price)
            
            await asyncio.sleep(300)
            # sleep for 5 minutes


    async def _start(self):
        self.running = True
        websocket_tast = asyncio.create_task(self.get_websocket_listener())
        update_task = asyncio.create_task(self.update_stock_data())

        await asyncio.gather(websocket_tast, update_task)
        
    async def _stop(self):
        self.running = False

    
