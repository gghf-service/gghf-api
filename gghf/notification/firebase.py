import firebase_admin
from firebase_admin import credentials, messaging
import json
import gghf.repository.subscribers.query

import logging
import logging.handlers as handlers
import time
import logging.config

cred = credentials.Certificate('private/serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('logger')

def message(game, store, latest_prices, previous_prices):
    messages = []
    for l_price in latest_prices:
        region_price = next(filter(lambda x: x['region'] == l_price['region'], previous_prices), None)
        if region_price is not None:
            # TODO set correct condition when send
            if l_price['final'] != region_price['final']:
                subscribers = gghf.repository.subscribers.query.get(appid=str(game['appid']), store=store, region=l_price['region'])
                print(len(subscribers))
                if subscribers:
                    topic = '{0}{1}{2}'.format(store, game['appid'], l_price['region'])

                    message = messaging.Message(
                        notification=messaging.Notification(
                            title= 'Changed the price',
                            body= 'The game "{0}" costs {1}{2}'.format(game['name'], l_price['final']/100, l_price['currency']),
                        ),
                        topic=topic,
                    )
                    messages.append(message)
    
    return messages

def bulk_send(messages):
    logger.info('Start send: ready {0} messages'.format(len(messages)))
    for msg in messages:
        response = messaging.send(msg)
        logger.warning('Message status: {0}'.format(response))
    
    logger.info('Finish send')