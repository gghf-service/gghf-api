from flask import Flask, request, jsonify, abort
import gghf.repository.subscribers
import gghf.repository.subscribers.query

app = Flask(__name__)

supported_stores = ['steam', 'playstation']

@app.route('/subscriber', methods=['POST'])
def create_subscriber():
    if not request.json:
        abort(400)

    update_operations = []
    r = request.json
    for item in r:
        device = item.get('device')
        store = item.get('store')
        appid = item.get('appid')
        region = item.get('region', 'US').upper()
        
        # TODO check if appid exist in db
        if device is not None and store is not None and store in supported_stores and appid is not None:
            update_operations.append(gghf.repository.subscribers.create(device, store, appid, region))
    
    gghf.repository.subscribers.bulk_update(update_operations)

    return jsonify(success=True)

@app.route('/subscriber', methods=['DELETE'])
def delete_subscriber():
    if not request.json:
        abort(400)

    update_operations = []
    r = request.json
    for item in r:
        device = item.get('device')
        store = item.get('store')
        appid = item.get('appid')
        region = item.get('region')
        
        if device is not None:
            update_operations.append(gghf.repository.subscribers.delete(device, store, appid, region))
    
    gghf.repository.subscribers.bulk_update(update_operations)

    return jsonify(success=True)

@app.route('/subscriber/<device>', methods=['PATCH'])
def update_subscriber(device):
    if device is None or not request.json:
        abort(400)

    r = request.json
    new_device = r.get('device')

    if new_device is not None:
        update_operations = []
        update_operations.append(gghf.repository.subscribers.action.update(device, new_device))
        gghf.repository.subscribers.bulk_update(update_operations)
        return jsonify(success=True)

    abort(400)

@app.route('/subscriber/<device>', methods=['GET'])
def get_subscriber(device):
    if device is None or not request.json:
        abort(400)

    r = request.args
    store = r.get('store')
    appid = r.get('appid')
    region = r.get('region')

    limit = int(r.get('limit', 0))
    offset = int(r.get('offset', 0))
    sort_by = r.get('sort_by')

    result = gghf.repository.subscribers.query.get(device, store, appid, region, limit, offset, sort_by)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
