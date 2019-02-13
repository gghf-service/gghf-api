import requests
import json
import gghf.parser.playstation.game 
import gghf.parser.playstation.price 
import os
import datetime
import watchdog.playstationdog
import gghf.notification.firebase
import gghf.repository.games.query

import logging
import logging.handlers as handlers
import time
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('logger')

current_platform = 'playstation'
current_store = 'playstation'

def parse_game(game):
    try:
        return gghf.parser.playstation.game.from_playstation(game)
    except Exception:
        logger.exception('Cannot parse game {0}'.format(game.get('id', '')))
        return None
    

def scrap(all_games):
    
    # playstation contains approximately 4000 games and price must be updated every day, so delay 10 sec between different games
    delay = 15
    rate_limit = 100
    
    for chunk in make_chunk(all_games, rate_limit):
        update_operations = []
        notification_operations = []

        for item in chunk:
            game = parse_game(item)
            logger.info('Parsed {0}'.format(game['appid']))
            
            # something went bad and we need to check the error log!
            if game is None:
                logger.warn('Game could not be parsed, look in the error logs {0}'.format(game['appid']))
                continue

            prices = watchdog.playstationdog.fetch_prices(item, delay)
            prices = watchdog.playstationdog.parse_prices(prices, game['appid'])
    
            # we assume if the game does not have US price, it is
            # not relevant to fetch prices for other countries
            if prices is None or not prices:
                logger.warn('App probably is free, skipping price fetch {0}'.format(game['appid']))
                update_operations.append(gghf.repository.games.update.make(game, [], current_store))
            else:
                operation = gghf.repository.games.update.make(game, prices, current_store)
                update_operations.append(operation)

            # get game from db if exists
            db_game = gghf.repository.games.query.get_game(game['appid'], current_platform, current_store)
            if db_game is not None:
                # add notification depends on region
                notification_operations.extend(gghf.notification.firebase.message(game, current_store, prices, db_game['price']))
                
        gghf.notification.firebase.bulk_send(notification_operations)
        gghf.repository.bulk_update(current_platform, update_operations)
        logger.info('Updated chunk')

def make_chunk(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def main():
    offset = 0
    amount = 99
    while True:
        all_games = []
        logger.info('Start scrap playstation games')
        while True:
            # use pagination to get all games
            try:
                games = requests.get('https://store.playstation.com/chihiro-api/viewfinder/US/en/999/STORE-MSF77008-ALLGAMES?start={0}&size={1}&gameContentType=games'.format(offset, amount)).text
                games = json.loads(games)['links']
            except Exception:
                games = None
                logger.exception('Cannot load page {0}'.format(offset/amount + 1))
                continue
            finally:
                offset += amount
            
            if not games:
                break     

            all_games.extend(games)

        logger.info('Finish scrap games, {0} pages'.format(offset/amount + 1))
        scrap(all_games)
        
                    

