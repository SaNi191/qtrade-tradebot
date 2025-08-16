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
        # specifically for updating previously existing stocks, not for adding new stocks
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
                threshold = new_price * float(self.stop_loss_ratio)
                stock.stop_loss_value = threshold
                stock.peak_value = new_price


    def _add_stock(self, new_ticker: str, new_price: float):
        # method to add new stocks; will throw a Runtime Error if given a stock that already exists
        new_ticker = new_ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.scalars(select(Stock.ticker).where(Stock.ticker == new_ticker)).first()

            if stock:
                raise RuntimeError("Stock already exists!")
            
            new_stock = Stock(ticker = new_ticker, current_value = new_price, peak_value = new_price, stop_loss_value = new_price * self.stop_loss_ratio)
            session.add(new_stock)

    def _remove_stock(self, ticker_to_remove: str):
        # method to remove a tracked ticker; will throw a Runtime Error if ticker does not exist
        ticker_to_remove = ticker_to_remove.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(ticker_to_remove)
            if not stock:
                raise RuntimeError(f"Stock with ticker {ticker_to_remove} does not exist!")
            session.delete(stock)



    @property
    def stop_loss_ratio(self) -> float:
        from utils.env_vars import STOPLOSS_RATIO

        if not STOPLOSS_RATIO:
            STOPLOSS_RATIO = 0.9
            # set the default STOPLOSS_RATIO to 90% of peak price

        return float(STOPLOSS_RATIO)

        



        
        
    


    
            




            



        

        













