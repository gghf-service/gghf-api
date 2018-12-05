import requests
import json
import time
from scrapper.steam import GameParser
import datetime
from pymongo import MongoClient, UpdateOne
import watchdog.steamdog
from config import Config

mongo = MongoClient(Config.MONGODB_URI)
db_name = Config.MONGODB_DATABASE


def make_update_operation(game, prices):
    game['price_latest'] = {'steam': prices}
    return UpdateOne({'appid': game['appid']}, {'$set': game}, upsert=True)


def bulk_update(updates):
    try:
        mongo[db_name].desktop_games.bulk_write(updates)
    except Exception as ex:
        print('Bulk update error', ex)


def parse_game(game, appid):
    try:
        return GameParser.from_steam(game, appid)
    except Exception as ex:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_filename = '{0}_steam_info.txt'.format(now)
        with open(error_filename, 'w') as f:
            f.write(appid)
            f.write('\n')
            f.write(game)
            f.flush()
        return None


def scrap(all_games):
    # steam allows 300 request per 5 minutes, so delay 15 sec between request
    delay = 15

    for game in all_games:
        appid = str(game['appid'])
        url = 'https://store.steampowered.com/api/appdetails?appids={0}&cc=us'.format(
            appid)
        fetched = requests.get(url).json()
        print('Fetched', appid)
        game = parse_game(fetched, appid)
        print('Parsed', appid)

        if game is None:
            time.sleep(delay)
            print('Game could not be parsed, look in the error logs', appid)
            continue

        if game['type'] != 'game' and game['type'] != 'dlc':
            print('Is not game neither dlc,', appid)
            time.sleep(delay)
            continue

        if fetched[appid]['data'].get('price_overview', None) is None:
            print('App probably is free, skipping price fetch', appid)
            bulk_update([make_update_operation(game, prices)])
            print('Updated', appid)
            time.sleep(delay)
            continue

        print('Fetching prices for', appid)
        time.sleep(delay)
        prices = watchdog.steamdog.fetch_prices([appid])
        prices = watchdog.steamdog.parse_prices(prices, [appid])

        # TODO: fetch games by chunks of 200 and make real bulk update
        bulk_update([make_update_operation(game, prices)])
        print('Updated', appid)


def main():
    while True:
        # TODO: maybe add my real steam api key?
        all_games = requests.get(
            'http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json').text
        all_games = json.loads(all_games)['applist']['apps']

        scrap(all_games)
