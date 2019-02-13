import pymongo
import gghf.repository.subscribers 

def get(device = None, store = None, appid = None, region = None, limit = 0, offset = 0, sort_by = None):
    query = {'sort': [], 'find': {}}

    if device is not None:
        query['find']['device'] = device

    if store is not None:
        query['find']['store'] = store

    if appid is not None:
        query['find']['appid'] = appid

    if region is not None:
        query['find']['region'] = region
    
    # sort_by format = sort_by=desc(created)
    if sort_by is not None:
        tokens = sort_by.split('(')
        key = tokens[0]
        value = pymongo.ASCENDING if tokens[1][:-1] == 'asc' else pymongo.DESCENDING
        query['sort'] = [(key, value)]
    else:
        query['sort'] = [('created', pymongo.DESCENDING)]
    
    found = gghf.repository.subscribers.db().find(query['find']).sort(query['sort']).limit(limit).skip(offset)

    result = []
    for subscriber in found:
        subscriber.pop('_id')
        result.append(subscriber)

    return result



