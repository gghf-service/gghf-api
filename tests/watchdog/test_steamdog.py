import watchdog.steamdog
import json


prices = None
test_app_changes = ['730', '65540']
test_regions = ['US', 'AR']


def test_fetch_prices():
    pass
    #prices = watchdog.steamdog.fetch_prices(test_app_changes, test_regions, 0)


def test_parse_prices():
    with open('tests/watchdog/steam_prices.json', 'r') as f:
        prices = json.loads(f.read())
        parsed = watchdog.steamdog.parse_prices(prices, test_app_changes)

        with open('tests/watchdog/db_prices.json', 'r') as db:
            db_prices = json.loads(db.read())
            assert len(parsed) == len(db_prices)

            for p in zip(parsed['730'], db_prices['730']):
                assert p[0]['store'] == p[1]['store']
                assert p[0]['region'] == p[1]['region']
                assert p[0]['initial'] == p[1]['initial']
                assert p[0]['currency'] == p[1]['currency']

