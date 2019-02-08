from pymongo import UpdateOne, DeleteMany
from datetime import datetime

def create(device, platform, appid, region):
    query = {'device': device, 'platform': platform, 'appid': appid, 'region': region, 'created': datetime.now()}
    return UpdateOne(query, {'$set': query}, upsert=True)

def delete(device, platform, appid, region):
    query = {'device': device}

    if platform is not None:
        query['platform'] = platform
    if appid is not None:
        query['appid'] = appid
    if region is not None:
        query['region'] = region
    return DeleteMany(query)