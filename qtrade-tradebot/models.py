from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import LargeBinary, TypeDecorator
from sqlalchemy import DateTime
from cryptography.fernet import Fernet
from env_vars import ENCRYPTION_KEY
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
    cache_ok = True

    def __init__(self, key: bytes):
        # passed to EncryptedToken from environment variable
        super().__init__()
        self.fernet_key = Fernet(key)

    def process_bind_param(self, value: str | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.encrypt(value.encode(encoding = "utf-8"))
    
    def process_result_value(self, value: bytes | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.decrypt(value).decode(encoding = "utf-8")
    
        
# contains encrypted refresh and access tokens
class Tokens(Base):
    __tablename__:str = "token_table"

    id:Mapped[int] = mapped_column(primary_key = True)

    # encrypted token value by key stored as environment variable
    refresh_token:Mapped[str] = mapped_column(EncryptedToken(ENCRYPTION_KEY), nullable = False)
    access_token: Mapped[str] = mapped_column(EncryptedToken(ENCRYPTION_KEY), nullable = False)
    # Tokens will not store the bootstrap case requiring manual authentification    
    api_server: Mapped[str] = mapped_column(nullable=False)
    # nullable as refresh tokens are one-time-use thus expiry_date is not relevant

    expiry_date:Mapped[datetime.datetime] = mapped_column(DateTime,nullable = False)
    # check for expiry upon request: if expired -> refresh using refresh_token
    # if refresh_token is invalid: error will occur -> logic to be implemented seperately


### TODO: add stock database to track max recorded price, stop-loss threshold, growth/decline
'''
class Stock(Base):
    # to be implemented
    pass
'''

