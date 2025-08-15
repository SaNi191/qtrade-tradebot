from models import Stock
from db import session_maker, session_manager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import Sequence, List

from utils.env_vars import STOPLOSS_RATIO


# StockTracker: 
# check tracked stocks (stocks within DB) with QTradeAPI 
# then match with DB to check stop loss 
# finally update values and send alert if threshold met
class StockTracker():
    def __init__(self, sessionmaker: sessionmaker):
        # SessionLocal stores sessionmaker that creates Sessions connecting to bot.db
        self.SessionLocal = sessionmaker


    def _get_tracked_stock_tickers(self) -> Sequence:
        # use to get a list of tickers (primary key) for tracked stocks (in database)
        with session_manager(self.SessionLocal) as session:
            return session.scalars(select(Stock.ticker)).unique().all()

    
    def check_stocks(self):
        # check tracked stocks using QTradeAPI
        tracked_stocks = self._get_tracked_stock_tickers()
        stocks_to_alert = []

        for ticker in tracked_stocks:
            # TODO: call method from QTradeAPI to get ticker info, then check for stop:loss 
            # if stop loss exceeded: append to stocks_to_alert
            # simultaneously: update stock data using self.update_stock()
            pass

    def _update_stock(self, ticker: str, new_price: float):
        # we only want to be able to update stocks internally through StockTracker
        # specifically for updating previously existing stocks, will not add unknown stocks
        ticker = ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.scalars(select(Stock.ticker).where(Stock.ticker == ticker)).first()
            if not stock:
                raise RuntimeError("Stock not found!")
            
            
            # update current value
            stock.current_value = new_price

            # if new value is greater than the peak value update stop loss thresholds
            if stock.peak_value < new_price:
                # update new peak_value
                from utils.env_vars import STOPLOSS_RATIO

                if not STOPLOSS_RATIO:
                    STOPLOSS_RATIO = 0.9
                    # set the default STOPLOSS_RATIO to 90% of peak price

                threshold = new_price * float(STOPLOSS_RATIO)
                stock.stop_loss_value = threshold
                stock.peak_value = new_price
        
        
    


    
            




            



        

        













