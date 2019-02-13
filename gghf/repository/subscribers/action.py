from pymongo import UpdateOne, DeleteMany, UpdateMany
from datetime import datetime

def create(device, store, appid, region):
    query = {'device': device, 'store': store, 'appid': appid, 'region': region, 'created_at': datetime.now()}
    return UpdateOne(query, {'$set': query}, upsert=True)

def delete(device, store, appid, region):
    query = {'device': device}

    if store is not None:
        query['store'] = store
    if appid is not None:
        query['appid'] = appid
    if region is not None:
        query['region'] = region

    return DeleteMany(query)

def update(device, new_device, store = None, appid = None, region = None):
    query = {'device': device}
    update = {'updated_at': datetime.now()}

    if new_device is not None:
        update['device'] = new_device
    if store is not None:
        update['store'] = store
    if appid is not None:
        update['appid'] = appid
    if region is not None:
        update['region'] = region
    
    return UpdateMany(query, {'$set': update})