import requests
import asyncio
import logging
import time

from database.token_manager import TokenManager
from database.stock_tracker import StockManager
from sqlalchemy.orm import sessionmaker

''' Websocket not implemented
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import connect
'''
# implementation of QTradeWorker
# - utilizes both StockTracker and TokenManager
# - adds async functionality and websocket connection to the QuestTrade API


logger = logging.getLogger(__name__)

class QTradeAPI():
    def __init__(self, sessionmaker: sessionmaker) -> None:
        self.token = TokenManager(sessionmaker)
        self.stocks = StockManager(sessionmaker)

        # for async relating to WebSocket, currently incomplete
        self._running = False
        self._change_lock = asyncio.Lock()
        self._latest_changes = {}

    @property
    def header(self):
        header = {
            'Authorization': f"Bearer {self.token.get_access_token()}"
        }
        return header
    
    def get_stock_symbol(self, ticker):
        # make REST API request to get symbol
        end_point = f'https://{self.token.get_api_server}/symbols/search'
        headers = self.header
        
        # REST API rate-limit is 20 requests a second 
        for attempt in range(3):
            # arbitrary number of attempts
            try:
                result = requests.get(end_point, headers = headers, params = {'prefix' : ticker})
                time.sleep(0.2)

                result.raise_for_status()
                result = result.json()
                if result:
                    return(result['symbol'][0]['symbolId'])
                else:
                    raise RuntimeError
                
            except requests.HTTPError as e:
                logger.error(f'Error: {e} occurred while retrieving object, retrying!')
                # possible refresh required
                token = self.token.get_access_token()
        
        raise RuntimeError('Failed to get response')
    
    def check_stock_info(self, stock_id) -> None:
        end_point = f'https://{self.token.get_api_server}/markets/quotes/'
        headers = self.header

        # REST API rate-limit is 20 requests a second; much faster to provide list of stock_ids
        for attempt in range(3):
            # arbitrary number of attempts
            try:
                result = requests.get(end_point, headers = headers, params = {'ids': stock_id})
                time.sleep(0.2)
                result.raise_for_status()
                result = result.json()
                if result:
                    #self.stocks.check_stock()
                    break
                else:
                    raise RuntimeError
                
            except requests.HTTPError as e:
                logger.error(f'Error: {e} occurred while retrieving object, retrying!')
                # possible refresh required
                token = self.token.get_access_token()

        raise RuntimeError('Failed to get response')
    
    def get_all_stocks(self):
        stock_list = self.stocks.get_tracked_stock_tickers()
        for stock in stock_list:
            stock_id = self.get_stock_symbol(stock)
            self.check_stock_info(stock_id)
            # get_stock_info


    ''' TODO: complete WebSocket streaming for live data feeds

    async def async_get_access_token(self):
        # since token.access_token is a property, use lambda to turn to func
        return await asyncio.to_thread(self.token.get_access_token)
    

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
    '''


            
        


        


    
