from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import LargeBinary
from sqlalchemy import DateTime
from typing import List
import time

# models for bot database:

    # Tokens:
        # id | value | expiry_date
    # note: id 1 will be refresh token; id 2 will be access token
    
    # Stock:
        # id | ticker | value | stop_loss


# define our Base
class Base(DeclarativeBase):
    pass


# contains encrypted refresh and access tokens
class Tokens(Base):
    __tablename__:str = "token_table"

    id:Mapped[int] = mapped_column(primary_key = True)

    # encrypted token value by key stored as environment variable
    value:Mapped[LargeBinary] = mapped_column(nullable=False)

    expiry_date:Mapped[DateTime] = mapped_column(nullable=False)


class Stock(Base):
    # to be implemented
    pass
