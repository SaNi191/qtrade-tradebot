from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import LargeBinary, TypeDecorator
from sqlalchemy import DateTime
from cryptography.fernet import Fernet
from env_vars import ENCRYPTION_KEY


# models for bot database:

    # Tokens:
        # id | value | expiry_date
    # note: id 1 will be refresh token; id 2 will be access token
    
    # Stock:
        # id | ticker | value | stop_loss


# define our Base
class Base(DeclarativeBase):
    pass

class EncryptedToken(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    def __init__(self, key: bytes):
        # passed to EncryptedToken from environment variable
        self.fernet_key = Fernet(key)

    def process_bind_param(self, value: str | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.encrypt(value.encode(encoding="utf-8"))
    
    def process_result_value(self, value: bytes | None, dialect):
        if value is None:
            return value
        else:
            return self.fernet_key.decrypt(value).decode(encoding="utf-8")
    
        

# contains encrypted refresh and access tokens
class Tokens(Base):
    __tablename__:str = "token_table"

    id:Mapped[int] = mapped_column(primary_key = True)

    # encrypted token value by key stored as environment variable
    value:Mapped[str] = mapped_column(EncryptedToken(ENCRYPTION_KEY), nullable=False)

    expiry_date:Mapped[DateTime] = mapped_column(nullable=False)


class Stock(Base):
    # to be implemented
    pass
