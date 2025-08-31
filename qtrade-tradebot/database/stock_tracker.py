import datetime
import logging

from alerts import get_alert_channel
from database.models import Stock
from database.db import session_manager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import Sequence

logger = logging.getLogger(__name__)

# StockTracker: 
# check tracked stocks (stocks within DB) with QTradeAPI 
# then match with DB to check stop loss 
# finally update values and send alert if threshold met
class StockManager():
    def __init__(self, sessionmaker: sessionmaker):
        # SessionLocal stores sessionmaker that creates Sessions connecting to bot.db
        # pass db.session_maker as sessionmaker
        self.SessionLocal = sessionmaker
        self.stocks_to_alert = []
    
    def _normalize_ticker(self, ticker: str) -> str:
        return ticker.strip().upper()
    
    def get_tracked_stock_tickers(self) -> Sequence:
        # use to get a list of tickers (primary key) for tracked stocks (in database)
        with session_manager(self.SessionLocal) as session:
            return session.scalars(select(Stock.ticker)).unique().all()

    def _update_stock(self, ticker: str, new_price: float) -> None:
        # specifically for updating previously existing stocks, not for adding new stocks
        ticker = ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(Stock, ticker)
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

    def alert_stocks(self) -> None:
        # TODO: 
        # - configure for other notification types
        # - implement user configuration (to control which email is notified)

        from utils.env_vars import EMAIL_TO_NOTIFY
        if not EMAIL_TO_NOTIFY:
            raise RuntimeError("No Email Provided!")
        

        email_alerter = get_alert_channel('email')
        subject = "Important: Stop-Loss Alert"
        msg = "Stop-loss Alert!\n"
        send_msg = False

        with session_manager(self.SessionLocal) as session:
            # loop through stock_list to alert
            stock_list = session.scalars(
                select(Stock)
                .where(Stock.ticker.in_(map(self._normalize_ticker, self.stocks_to_alert)))
            ).all()
            
            for stock in stock_list:
                if not stock.last_notified or datetime.datetime.now() - stock.last_notified >= datetime.timedelta(days = 1):
                    # only notify a stock once per day
                    stock.last_notified = datetime.datetime.now()
                    send_msg = True
                    msg += f"{stock.ticker} (${stock.current_value}) has reached stop-loss threshold of ${stock.stop_loss_value} \n"

        # if not send_msg then no stocks need to be notified
        if send_msg:
            email_alerter.send_msg(msg = msg, recipient = EMAIL_TO_NOTIFY, subject = subject)

        self.stocks_to_alert.clear()

    def check_stock(self, stock_ticker: str, stock_price) -> None:
        # check given stock then alert 
        stock_ticker = self._normalize_ticker(stock_ticker)
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(Stock, stock_ticker)
            if not stock:
                raise RuntimeError("Stock not found in db")

            if stock.stop_loss_value > stock_price and stock_ticker not in self.stocks_to_alert:
                # need to alert the stock
                self.stocks_to_alert.append(stock_ticker)

        self._update_stock(stock_ticker, stock_price)
        
    
    def add_stock(self, new_ticker: str, new_price: float, stock_currency: str) -> None:
        # method to add new stocks; will throw a Runtime Error if given a stock that already exists
        new_ticker = new_ticker.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(Stock, new_ticker)
            if stock:
                raise RuntimeError(f"Stock with ticker {new_ticker} already exists!")
            
            new_stock = Stock(
                ticker = self._normalize_ticker(new_ticker), 
                current_value = new_price, 
                peak_value = new_price, 
                stop_loss_value = new_price * self.stop_loss_ratio,
                stock_currency = stock_currency
            )

            session.add(new_stock)

    def remove_stock(self, ticker_to_remove: str) -> None:
        # method to remove a tracked ticker; will throw a Runtime Error if ticker does not exist
        ticker_to_remove = ticker_to_remove.upper()
        with session_manager(self.SessionLocal) as session:
            stock: Stock = session.get(Stock, ticker_to_remove)
            if not stock:
                raise RuntimeError(f"Stock with ticker {ticker_to_remove} does not exist!")
            session.delete(stock)


    @property
    def stop_loss_ratio(self) -> float:
        from utils.env_vars import STOPLOSS_RATIO
        return float(STOPLOSS_RATIO) if STOPLOSS_RATIO else 0.9
    

    
