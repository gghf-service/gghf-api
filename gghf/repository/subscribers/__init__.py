from gghf.repository.subscribers.action import create, delete, update
from gghf.repository.subscribers.query import get

from config import Config
import pymongo
from pymongo import MongoClient

import logging
import logging.handlers as handlers
import time
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('logger')

mongo = MongoClient(Config.MONGODB_URI)
db_name = Config.MONGODB_DATABASE

def db():
    return mongo[db_name].subscribers

def bulk_update(updates):
    try:
        db().bulk_write(updates)
    except Exception:
        logger.exception('Bulk update error')
