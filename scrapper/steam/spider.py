import requests
import json
import time
from scrapper.steam import GameParser
import datetime
from pymongo import MongoClient, UpdateOne
from watchdog.steamdog.parser import PriceParser
from config import Config

mongo = MongoClient(Config.MONGODB_URI)
db_name = Config.MONGODB_DATABASE


def make_update_operation(game, price):
    game['price_latest'] = {'steam': [price]}
    return UpdateOne({'appid': game['appid']}, {'$set': game}, upsert=True)


def bulk_update(updates):
    try:
        mongo[db_name].desktop_games.bulk_write(updates)
    except Exception as ex:
        print('Bulk update error', ex)


def parse_game(game, appid):
    try:
        parsed = json.loads(game)
        result = GameParser.from_steam(parsed, appid)
        parsed['region'] = 'us'
        price = PriceParser.from_steam(parsed, appid)
        return result, price
    except Exception as ex:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_filename = '{0}_steam_info.txt'.format(now)
        with open(error_filename, 'w') as f:
            f.write(str(appid))
            f.write('\n')
            f.write(game)
        return None, None


def scrap(all_games):
    # stealm allows 300 request per 5 minutes, so delay 15 sec between request
    delay = 15

    for game in all_games:
        appid = game['appid']
        url = 'https://store.steampowered.com/api/appdetails?appids={0}&cc=us'.format(
            appid)
        fetched = requests.get(url).text
        print('Fetched', appid)
        game, price = parse_game(fetched, appid)
        print('Parsed', appid)

        if game is None:
            continue

        # TODO: fetch games by chunks of 200 and make real bulk update
        bulk_update([make_update_operation(game, price)])
        print('Updated', appid)
        time.sleep(delay)


def main():
    while True:
        # TODO: maybe add my real steam api key?
        all_games = requests.get(
            'http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json').text
        all_games = json.loads(all_games)['applist']['apps']

        scrap(all_games)
