import requests
import json
import time
from scrapper.steam import GameParser
import datetime

def parse_game(game, appid):
    try:
        parsed = json.loads(game)
        parsed = GameParser.from_steam(parsed, appid)
        return parsed
    except Exception as ex:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_filename = '{0}_steam_info.txt'.format(now)
        with open(error_filename, 'w') as f:
                f.write(str(appid))
                f.write('\n')
                f.write(game)
        return None

def scrap(all_games):
    # stealm allows 300 request per 5 minutes, so delay 15 sec between request
    delay = 15

    for game in all_games:
        appid = game['appid']
        url = 'https://store.steampowered.com/api/appdetails?appids={0}&cc=us'.format(appid)
        fetched = requests.get(url).text
        parsed = parse_game(fetched, appid)
        # insert to db
        time.sleep(delay)

def main():
    while True:
        # TODO: maybe add my real steam api key?
        all_games = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json').text
        all_games = json.loads(all_games)['applist']['apps']

        scrap(all_games)