from gghf.repository.subscribers.action import create, delete
from config import Config
import pymongo
from pymongo import MongoClient
import logging
import logging.handlers as handlers
import time
import logging.config
import gghf.repository.subscribers.query
from gghf.repository import db_subscribers

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('logger')

mongo = MongoClient(Config.MONGODB_URI)
db_name = Config.MONGODB_DATABASE


def bulk_update(updates):
    try:
        db_subscribers().bulk_write(updates)
    except Exception:
        logger.exception('Bulk update error')

