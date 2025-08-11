from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import LargeBinary, TypeDecorator, Numeric
from sqlalchemy import DateTime
from cryptography.fernet import Fernet
from utils.env_vars import ENCRYPTION_KEY
import datetime

# Purpose: define database models for SQLAlchemy

# models for bot database:

    # Tokens:
        # id | refresh_token | access_token | expiry_date
    
    # Stock:
        # ticker (primary key) | current_value | peak_value | stop_loss_threshold
        # use ticker as primary key as it will always be unique

# define our Base
class Base(DeclarativeBase):
    pass

# customized encrypted token class built upon LargeBinary
class EncryptedToken(TypeDecorator):
    impl = LargeBinary
    # indicates that LargeBinary is the class to be built upon and stored within DB
    cache_ok = True

    def __init__(self, key: bytes):
        # passed to EncryptedToken from environment variable
        super().__init__()
        self.fernet_key = Fernet(key)

    # process for binding to EncryptedToken
    def process_bind_param(self, value: str | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.encrypt(value.encode(encoding = "utf-8"))
    
    # process for retriving EncryptedToken
    def process_result_value(self, value: bytes | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.decrypt(value).decode(encoding = "utf-8")

        
# contains encrypted refresh and access tokens
class Token(Base):
    __tablename__:str = "token_table"

    id:Mapped[int] = mapped_column(primary_key = True)

    # encrypted token value by key stored as environment variable
    refresh_token:Mapped[str] = mapped_column(EncryptedToken(ENCRYPTION_KEY), nullable = False)
    # maps str to EncryptedToken (overridden class)
    access_token: Mapped[str] = mapped_column(EncryptedToken(ENCRYPTION_KEY), nullable = False)
    # Tokens will not store the bootstrap case requiring manual authentification    
    api_server: Mapped[str] = mapped_column(nullable = False)
    # nullable as refresh tokens are one-time-use thus expiry_date is not relevant

    expiry_date:Mapped[datetime.datetime] = mapped_column(DateTime, nullable = False)
    # check for expiry upon request: if expired -> refresh using refresh_token
    # if refresh_token is invalid: error will occur -> logic to be implemented seperately


### TODO: add stock database to track max recorded price, stop-loss threshold, growth/decline

class Stock(Base):
    __tablename__:str = "stock_table"

    # use the ticker as primary key
    ticker:Mapped[str] = mapped_column(primary_key = True)

    current_value:Mapped[float] = mapped_column(Numeric(), nullable = False)
    peak_value:Mapped[float] = mapped_column(Numeric(), nullable = False)
    stop_loss_value:Mapped[float] = mapped_column(Numeric(), nullable = False)





