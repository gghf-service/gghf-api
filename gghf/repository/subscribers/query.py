import pymongo
from gghf.repository import db_subscribers

def get(device, platform, appid, region, limit, offset, sort_by):
    query = {'sort': [], 'find': {'device': device}}

    if platform is not None:
        query['find']['platform'] = platform

    if appid is not None:
        query['find']['appid'] = appid
        print(query)

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

    found = db_subscribers().find(query['find']).sort(query['sort']).limit(limit).skip(offset)

    result = []
    for subscriber in found:
        subscriber.pop('_id')
        result.append(subscriber)

    return result



