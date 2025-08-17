from alerts import get_alert_channel
from alerts.email_utils import EmailAlert

from models import Stock
from db import session_maker, session_manager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import Sequence, List, Tuple



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


    def _update_stock(self, ticker: str, new_price: float):
        # we only want to be able to update stocks internally through StockTracker
        # specifically for updating previously existing stocks, not for adding new stocks
        ticker = ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(ticker)
            if not stock:
                raise RuntimeError(f"Stock with ticker {ticker} not found!")
            
            # update current value
            stock.current_value = new_price

            # if new value is greater than the peak value update stop loss thresholds
            if stock.peak_value < new_price:
                # update new peak_value
                threshold = new_price * float(self.stop_loss_ratio)
                stock.stop_loss_value = threshold
                stock.peak_value = new_price

    def _alert_stocks(self, stock_list: List[Tuple[Stock, float, float]]):
        # TODO: 
        # - configure for other notification types, 
        # - implement user configuration (control which email is notified)


        from utils.env_vars import EMAIL_TO_NOTIFY
        if not EMAIL_TO_NOTIFY:
            raise RuntimeError("No Email Provided!")
        

        email_alerter = get_alert_channel('email')
        subject = "Important: Stop-Loss Alert"
        msg = "Stop-loss Alert!\n"

        # loop through stock_list to alert
        for stock_ticker, stop_loss, cur_price in stock_list:
            msg += f"{stock_ticker} (${cur_price}) (has reached stop-loss threshold of ${stop_loss} \n"
        

        email_alerter.send_msg(msg = msg, recipient = EMAIL_TO_NOTIFY, subject = subject)





    def check_stocks(self) -> None:
        # check tracked stocks using QTradeAPI
        tracked_stocks = self._get_tracked_stock_tickers()
        stocks_to_alert = []

        # This can be done with a SQLAlchemy command
        for ticker in tracked_stocks:
            # TODO: call method from QTradeAPI to get ticker info, then check for stop:loss 
            # if stop loss exceeded: append to stocks_to_alert
            # simultaneously: update stock data using self._update_stock()
            pass

        self._alert_stocks(stocks_to_alert)
    
    def add_stock(self, new_ticker: str, new_price: float) -> None:
        # method to add new stocks; will throw a Runtime Error if given a stock that already exists
        new_ticker = new_ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(new_ticker)

            if stock:
                raise RuntimeError(f"Stock with ticker {new_ticker} already exists!")
            
            new_stock = Stock(ticker = new_ticker, current_value = new_price, peak_value = new_price, stop_loss_value = new_price * self.stop_loss_ratio)
            session.add(new_stock)

    def remove_stock(self, ticker_to_remove: str) -> None:
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

        



        
        
    


    
            




            



        

        













