from flask import Flask, request, jsonify, abort
import gghf.repository.subscribers
import gghf.repository.subscribers.query

app = Flask(__name__)

supported_plarform = ['steam', 'playstation']

@app.route('/subscriber', methods=['POST'])
def create_subscriber():
    if not request.json:
        abort(400)

    update_operations = []
    r = request.json
    for item in r:
        device = item.get('device')
        platform = item.get('platform')
        appid = item.get('appid')
        region = item.get('region', 'us')
        
        # TODO check if appid exist in db
        if device is not None and platform is not None and appid is not None:
            update_operations.append(gghf.repository.subscribers.create(device, platform, appid, region))
    
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
        platform = item.get('platform')
        appid = item.get('appid')
        region = item.get('region')
        
        if device is not None:
            update_operations.append(gghf.repository.subscribers.delete(device, platform, appid, region))
    
    gghf.repository.subscribers.bulk_update(update_operations)

    return jsonify(success=True)

@app.route('/subscriber/<device>', methods=['GET'])
def get_subscriber(device):
    if device is None:
        abort(400)

    r = request.args
    platform = r.get('platform')
    appid = r.get('appid')
    region = r.get('region')

    limit = int(r.get('limit', 0))
    offset = int(r.get('offset', 0))
    sort_by = r.get('sort_by')

    result = gghf.repository.subscribers.query.get(device, platform, appid, region, limit, offset, sort_by)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
