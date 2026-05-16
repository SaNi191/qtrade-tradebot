# tests/test_db_managers.py
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import datetime

from database.db import session_manager
from database.models import Token, Stock
from database.token_manager import TokenManager
from database.stock_tracker import StockManager

# ------------------------
# Dummy sessionmaker setup
# ------------------------
class DummySessionMaker:
    """Callable sessionmaker that returns a MagicMock session"""
    def __call__(self):
        return MagicMock()

@pytest.fixture
def mock_token():
    """Returns a dummy Token object"""
    return Token(
        id=1,
        access_token="access123",
        refresh_token="refresh123",
        api_server="api.test.com",
        expiry_date=datetime.datetime.now() + datetime.timedelta(hours=1)
    )

@pytest.fixture
def expired_token():
    """Returns an expired Token object"""
    return Token(
        id=1,
        access_token="expired_access",
        refresh_token="expired_refresh",
        api_server="api.test.com",
        expiry_date=datetime.datetime.now() - datetime.timedelta(hours=1)
    )

@pytest.fixture
def token_manager(mock_token):
    """Return TokenManager with mocked session_manager"""
    with patch("database.db.session_manager") as mock_sess_mgr:
        mock_session = MagicMock()
        mock_session.get.return_value = mock_token
        mock_sess_mgr.return_value.__enter__.return_value = mock_session
        tm = TokenManager(sessionmaker=DummySessionMaker())
        tm._get_token = MagicMock(return_value=mock_token)  # override _get_token
        yield tm

@pytest.fixture
def stock_manager():
    """Return StockManager with mocked session_manager"""
    with patch("database.db.session_manager") as mock_sess_mgr:
        mock_session = MagicMock()
        mock_sess_mgr.return_value.__enter__.return_value = mock_session
        sm = StockManager(sessionmaker=DummySessionMaker())
        yield sm

# ------------------------
# TokenManager tests
# ------------------------
def test_get_access_token_not_expired(token_manager, mock_token):
    token_manager._get_token = MagicMock(return_value=mock_token)
    result = token_manager.get_access_token()
    assert result == "access123"

def test_get_access_token_expired_triggers_refresh(token_manager, expired_token):
    # patch _get_token to return expired token
    token_manager._get_token = MagicMock(return_value=expired_token)
    token_manager._refresh_tokens = MagicMock()
    result = token_manager.get_access_token()
    # _refresh_tokens should have been called because token is expired
    token_manager._refresh_tokens.assert_called_once()
    
def test_get_refresh_token(token_manager, mock_token):
    token_manager._get_token = MagicMock(return_value=mock_token)
    result = token_manager.get_refresh_token()
    assert result == "refresh123"

def test_get_api_server(token_manager, mock_token):
    with patch("database.db.session_manager") as mock_sess_mgr:
        mock_session = MagicMock()
        mock_session.get.return_value = mock_token
        mock_sess_mgr.return_value.__enter__.return_value = mock_session
        result = token_manager.get_api_server()
        assert result == "api.test.com"

# ------------------------
# StockManager tests
# ------------------------
def test_add_stock_success(stock_manager):
    new_stock_session = MagicMock()
    new_stock_session.get.return_value = None  # stock doesn't exist
    stock_manager.stop_loss_ratio = 0.9  # patch ratio
    with patch("database.db.session_manager", return_value=MagicMock(__enter__=lambda s: new_stock_session, __exit__=lambda s,e,t,tb: None)):
        stock_manager.add_stock("MSFT", 200, "USD")
        new_stock_session.add.assert_called_once()
        added_stock = new_stock_session.add.call_args[0][0]
        assert added_stock.ticker == "MSFT"

def test_add_stock_failure(stock_manager):
    # stock already exists
    existing_stock = MagicMock()
    existing_stock.ticker = "AAPL"
    stock_session = MagicMock()
    stock_session.get.return_value = existing_stock
    with patch("database.db.session_manager", return_value=MagicMock(__enter__=lambda s: stock_session, __exit__=lambda s,e,t,tb: None)):
        with pytest.raises(RuntimeError):
            stock_manager.add_stock("AAPL", 150, "USD")

def test_check_stock_triggers_alert(stock_manager):
    # setup stock below stop-loss
    stock = MagicMock()
    stock.stop_loss_value = 100
    stock.current_value = 90
    stock.peak_value = 120
    stock_manager.stocks_to_alert = []
    session_mock = MagicMock()
    session_mock.get.return_value = stock
    with patch("database.db.session_manager", return_value=MagicMock(__enter__=lambda s: session_mock, __exit__=lambda s,e,t,tb: None)):
        stock_manager._update_stock = MagicMock()
        stock_manager.check_stock("TEST", 80)
        assert "TEST" in stock_manager.stocks_to_alert

def test_check_stock_no_alert(stock_manager):
    # setup stock above stop-loss
    stock = MagicMock()
    stock.stop_loss_value = 100
    stock.current_value = 150
    stock.peak_value = 150
    stock_manager.stocks_to_alert = []
    session_mock = MagicMock()
    session_mock.get.return_value = stock
    with patch("database.db.session_manager", return_value=MagicMock(__enter__=lambda s: session_mock, __exit__=lambda s,e,t,tb: None)):
        stock_manager._update_stock = MagicMock()
        stock_manager.check_stock("TEST", 200)
        assert stock_manager.stocks_to_alert == []

def test_remove_stock_success(stock_manager):
    stock = MagicMock()
    session_mock = MagicMock()
    session_mock.get.return_value = stock
    with patch("database.db.session_manager", return_value=session_mock) as session:
        stock_manager.remove_stock("TEST")
        session.delete.assert_called_once_with(stock)

def test_remove_stock_failure(stock_manager):
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with patch("database.db.session_manager", return_value=MagicMock(__enter__=lambda s: session_mock, __exit__=lambda s,e,t,tb: None)):
        with pytest.raises(RuntimeError):
            stock_manager.remove_stock("TEST")
