from dataclasses import dataclass
from loguru import logger as log


DEPOSIT = "deposit"
WITHDRAW = "withdraw"
# LOG_PATH = "/var/log/balance_api/api.log"
LOG_PATH = "logs/api.log"
LOG_FORMAT = "{time:YYYY:MMM:DD:ddd:HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
log.add(LOG_PATH, format=LOG_FORMAT)


@dataclass(frozen=True)
class Config:
    LOG: log = log
    DEBUG: bool = False
    HOST: str = 'localhost'
    PORT: int = 8000
    DATABASE_URI: str = 'postgresql://username:password@localhost/dbname'
