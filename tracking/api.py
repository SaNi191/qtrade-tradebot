import requests
import asyncio
import logging
import time

from typing import List, Dict, Any, Iterable
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
REQUEST_TIMEOUT = 15

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
        ticker = ticker.strip().upper()
        end_point = f'{self._base_url()}/v1/symbols/search'
        headers = self.header
        
        # REST API rate-limit is 20 requests a second 
        for attempt in range(3):
            # arbitrary number of attempts
            try:
                result = requests.get(
                    end_point,
                    headers=headers,
                    params={'prefix': ticker},
                    timeout=REQUEST_TIMEOUT,
                )
                time.sleep(0.2)

                result.raise_for_status()
                result = result.json()
                symbols = result.get('symbols') or result.get('symbol') or []
                if symbols:
                    return symbols[0]['symbolId']
                else:
                    raise RuntimeError(f"No Questrade symbol found for {ticker}.")
                
            except requests.RequestException as e:
                logger.error(f'Error: {e} occurred while retrieving object, retrying!')
                # possible refresh required
                token = self.token.get_access_token()
        
        raise RuntimeError('Failed to get response')
    
    def check_stock_info(self, id_list: List[int]) -> None:
        if not id_list:
            return

        end_point = f'{self._base_url()}/v1/markets/quotes/'
        headers = self.header

        # REST API rate-limit is 20 requests a second; much more efficient to provide list of stock_ids
        for attempt in range(3):
            # arbitrary number of attempts
            try:
                result = requests.get(
                    end_point,
                    headers=headers,
                    params={'ids': ",".join(map(str, id_list))},
                    timeout=REQUEST_TIMEOUT,
                )
                # will return a dict where the stock key contains a list of stocks given by id
                time.sleep(0.2)
                result.raise_for_status()
                result = result.json()
                if result:
                    for stock in result.get('quotes', []):
                        # changed Ticker limitations to allow for a greater 
                        # range of tickers (ie. > 5 chars)
                        stock_ticker = stock['symbol']
                        stock_price = self._quote_price(stock)
                        if stock_price is None:
                            logger.warning(f"Skipping {stock_ticker}: quote did not include a usable price.")
                            continue
                        # cache symbol id when present
                        try:
                            sym_id = stock.get('symbolId')
                            if sym_id is not None:
                                self.stocks.set_symbol_id_for(stock_ticker, int(sym_id))
                        except Exception:
                            pass
                        self.stocks.check_stock(stock_ticker, stock_price)
                    return
                else:
                    logger.error(f'Error: result was empty.')
                    # will automatically try again
                
            except requests.RequestException as e:
                logger.error(f'Error: {e} occurred while retrieving object, retrying!')
                # possible refresh required
                token = self.token.get_access_token()

        raise RuntimeError('Failed to get response')
    
    def get_all_stocks(self):
        stock_list = self.stocks.get_tracked_stock_tickers()
        # prefer cached ids
        id_list: List[int] = []
        missing: List[str] = []
        for stock in stock_list:
            stock_id = self.stocks.get_symbol_id_for(stock)
            if stock_id is None:
                missing.append(stock)
            else:
                id_list.append(stock_id)
        if missing:
            resolved = self.lookup_symbol_ids(missing)
            for ticker, stock_id in resolved.items():
                try:
                    self.stocks.set_symbol_id_for(ticker, stock_id)
                    id_list.append(stock_id)
                except Exception:
                    continue
        self.check_stock_info(id_list)

    # -----------------------------
    # Questrade account integration
    # -----------------------------
    def _base_url(self) -> str:
        get_api_server = self.token.get_api_server
        api_server = get_api_server() if callable(get_api_server) else get_api_server
        api_server = str(api_server).rstrip("/")
        if api_server.startswith(("http://", "https://")):
            return api_server.removesuffix("/v1")
        return f"https://{api_server.removesuffix('/v1')}"

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = f"{self._base_url()}{path}"
        headers = self.header
        for attempt in range(3):
            resp = None
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
                time.sleep(0.2)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                logger.error(f"GET {path} failed: {e}; attempt {attempt+1}/3")
                # force token refresh on 401
                if resp is not None and resp.status_code == 401:
                    _ = self.token.get_access_token()
        raise RuntimeError(f"Failed to GET {path}")

    def get_accounts(self) -> List[Dict[str, Any]]:
        data = self._get("/v1/accounts")
        return data.get("accounts", [])

    def get_positions(self, account_id: str) -> List[Dict[str, Any]]:
        data = self._get(f"/v1/accounts/{account_id}/positions")
        return data.get("positions", [])

    def get_positions_all_accounts(self) -> List[Dict[str, Any]]:
        positions: List[Dict[str, Any]] = []
        for acct in self.get_accounts():
            acct_id = acct.get("number")
            if not acct_id:
                continue
            positions.extend(self.get_positions(str(acct_id)))
        return positions

    def _extract_ticker_currency(self, position: Dict[str, Any]) -> tuple[str, str]:
        # Questrade position symbol format may include suffixes; prefer 'symbol'
        symbol = position.get("symbol")
        if not symbol:
            raise RuntimeError("Position missing symbol")
        currency = position.get("currency") or position.get("currentMarketValueCurrency") or "USD"
        return str(symbol).upper(), str(currency).upper()

    def _batch(self, iterable: Iterable[Any], size: int) -> Iterable[List[Any]]:
        batch: List[Any] = []
        for item in iterable:
            batch.append(item)
            if len(batch) >= size:
                yield batch
                batch = []
        if batch:
            yield batch

    def _quote_price(self, quote: Dict[str, Any]) -> float | None:
        price = quote.get("lastTradePrice") or quote.get("bidPrice") or quote.get("askPrice")
        return float(price) if price is not None else None

    def lookup_symbol_ids(self, tickers: List[str]) -> Dict[str, int]:
        # Use symbols/search per ticker due to API; cache as needed
        mapping: Dict[str, int] = {}
        for ticker in tickers:
            try:
                mapping[ticker] = self.get_stock_symbol(ticker)
            except Exception:
                logger.warning(f"Could not resolve symbol id for {ticker}")
        return mapping

    def sync_tracked_from_accounts(self) -> None:
        """
        Fetch user positions from all Questrade accounts and upsert into the Stock table.
        Existing stocks are not removed. New positions are added with current price lookup and
        default stop-loss ratio. If a position already exists, it is left unchanged here.
        """
        positions = self.get_positions_all_accounts()
        # unique set of tickers
        ticker_currency: Dict[str, str] = {}
        for pos in positions:
            try:
                ticker, currency = self._extract_ticker_currency(pos)
                ticker_currency[ticker] = currency
            except Exception as e:
                logger.warning(f"Skipping position due to parse error: {e}")

        # Add any missing tickers to DB with a price snapshot via quotes
        existing = set(self.stocks.get_tracked_stock_tickers())
        to_add = [t for t in ticker_currency.keys() if t not in existing]
        if not to_add:
            logger.info("No new symbols to add from Questrade positions")
            return

        # Resolve ids and fetch quotes in batches
        id_map = self.lookup_symbol_ids(to_add)
        ids = list(id_map.values())
        if not ids:
            logger.info("No symbol ids resolved for new tickers")
            return

        # Fetch quotes in chunks and add
        # Reuse check_stock_info to update values? Here we need prices, so query directly
        quotes_url = f"{self._base_url()}/v1/markets/quotes/"
        headers = self.header
        prices: Dict[int, float] = {}
        for chunk in self._batch(ids, 50):
            for attempt in range(3):
                resp = None
                try:
                    resp = requests.get(
                        quotes_url,
                        headers=headers,
                        params={"ids": ",".join(map(str, chunk))},
                        timeout=REQUEST_TIMEOUT,
                    )
                    time.sleep(0.2)
                    resp.raise_for_status()
                    data = resp.json()
                    for q in data.get("quotes", []):
                        price = self._quote_price(q)
                        if price is not None:
                            prices[q["symbolId"]] = price
                    break
                except requests.RequestException as e:
                    logger.error(f"quotes fetch failed: {e}")
                    if resp is not None and resp.status_code == 401:
                        _ = self.token.get_access_token()

        # Add to DB
        for ticker in to_add:
            sym_id = id_map.get(ticker)
            price = prices.get(sym_id, 0.0)
            currency = ticker_currency.get(ticker, "USD")
            try:
                self.stocks.add_stock(ticker, float(price), currency)
                logger.info(f"Added {ticker} at {price} {currency} from Questrade positions")
            except RuntimeError:
                # already exists or other validation issue
                logger.warning(f"Failed to add {ticker}: already exists or validation error")
                continue

    # -----------------------------
    # GUI-facing helpers
    # -----------------------------
    def _get_quotes_by_ids(self, ids: List[int]) -> Dict[int, Dict[str, Any]]:
        quotes_url = f"{self._base_url()}/v1/markets/quotes/"
        headers = self.header
        result: Dict[int, Dict[str, Any]] = {}
        for chunk in self._batch(ids, 50):
            for attempt in range(3):
                resp = None
                try:
                    resp = requests.get(
                        quotes_url,
                        headers=headers,
                        params={"ids": ",".join(map(str, chunk))},
                        timeout=REQUEST_TIMEOUT,
                    )
                    time.sleep(0.2)
                    resp.raise_for_status()
                    data = resp.json()
                    for q in data.get("quotes", []):
                        result[q["symbolId"]] = q
                    break
                except requests.RequestException as e:
                    logger.error(f"quotes fetch failed: {e}")
                    if resp is not None and resp.status_code == 401:
                        _ = self.token.get_access_token()
        return result

    def add_tracked_stock(self, ticker: str, currency: str | None = None) -> None:
        """Add a new tracked stock by ticker. Resolves symbolId, fetches current price, and caches symbolId."""
        # normalize the ticker
        ticker = ticker.strip().upper() 
        sym_id = self.stocks.get_symbol_id_for(ticker)
        if sym_id is None:
            sym_id = self.get_stock_symbol(ticker)

        quotes = self._get_quotes_by_ids([sym_id])
        q = quotes.get(sym_id, {})
        price = self._quote_price(q)
        if price is None:
            raise RuntimeError(f"Could not get a usable quote price for {ticker}.")
        use_currency = currency or q.get("currency") or "USD"

        # add to DB
        self.stocks.add_stock(ticker, float(price), str(use_currency).upper())
        # ensure cache persisted
        try:
            self.stocks.set_symbol_id_for(ticker, int(sym_id))
        except Exception:
            pass

    def remove_tracked_stock(self, ticker: str) -> None:
        """Remove a tracked stock by ticker."""
        logger.info(f"Removing tracked stock: {ticker}")
        self.stocks.remove_stock(ticker)
        logger.info(f"Successfully removed tracked stock: {ticker}")









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


            
        


        


    
