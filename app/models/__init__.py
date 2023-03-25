from gino import Gino
import uuid
from sqlalchemy import Enum, Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), default='noname')
    balance = Column(Numeric(precision=10, scale=2), default='0.00')


class Transaction(db.Model):
    __tablename__ = "transactions"

    uid = Column(UUID(), primary_key=True, default=uuid.uuid4())
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    timestamp = Column(DateTime, nullable=False)
