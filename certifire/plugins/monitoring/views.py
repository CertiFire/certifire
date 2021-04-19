import json

from certifire import app, auth, database
from certifire.plugins.monitoring.models import Target, Worker
from flask import abort, g, jsonify, request, url_for

@app.route('/api/target', methods=['POST'])
@auth.login_required
def new_mon_target():
    post_data = post_data = request.form
    ip = post_data.get('ip')
    host = post_data.get('host')
    url = post_data.get('url')
    if not ip and not host:
        post_data = request.get_json(force=True)
        ip = post_data.get('ip')
        host = post_data.get('host')
        url = post_data.get('url')
    
    if not ip and not host:
        return (jsonify({'status': 'host or ip fields missing'}), 400)
    
    T = Target(ip, host, url)
    ret, tid = T.create()
    
    if ret:
        status = json.loads(T.json)
        return (jsonify(status), 201,
        {'Location': url_for('get_mon_target', id=tid, _external=True),
                 'target_id': tid})
    else:
        return (jsonify({'status': 'Internal Error'}), 400)

@app.route('/api/target/<int:id>')
@auth.login_required
def get_mon_target(id):
    T = Target.query.get(id)
    if not T:
        abort(400)

    ret = json.loads(T.json)
    return jsonify(ret)

@app.route('/api/target/<int:id>', methods=['DELETE'])
@auth.login_required
def del_mon_target(id):
    T = Target.query.get(id)
    if not T:
        abort(400)

    ret = T.delete()
    if ret:
        return (jsonify({'status': 'Target deleted'}), 200)
    else:
        return (jsonify({'status': 'Failed to delete'}), 400)

@app.route('/api/target')
@auth.login_required
def get_all_targets():
    data = {}
    targets = database.select_all(Target)
    for target in targets:
        data[target.id] = json.loads(target.json)
    return jsonify(data)

@app.route('/api/worker', methods=['POST'])
@auth.login_required
def new_mon_worker():
    post_data = post_data = request.form
    ip = post_data.get('ip')
    host = post_data.get('host')
    location = post_data.get('location')
    mon_self = post_data.get('mon_self', False)
    create_host = post_data.get('create_host', False)
    if not ip and not host:
        post_data = request.get_json(force=True)
        ip = post_data.get('ip')
        host = post_data.get('host')
        location = post_data.get('location')
        mon_self = post_data.get('mon_self', False)
        create_host = post_data.get('create_host', False)
    
    if not ip and not host:
        return (jsonify({'status': 'host or ip fields missing'}), 400)
    
    if not location:
        return (jsonify({'status': 'location field missing'}), 400)
    
    W = Worker(ip, host, location, mon_self)
    ret = W.create(create_host)
    
    if ret:
        status = json.loads(W.json)
        return (jsonify(status), 201,
        {'Location': url_for('get_mon_worker', id=W.id, _external=True),
                 'worker_id': W.id})
    else:
        return (jsonify({'status': 'Internal Error'}), 400)

@app.route('/api/worker/<int:id>')
@auth.login_required
def get_mon_worker(id):
    W = Worker.query.get(id)
    if not W:
        abort(400)

    ret = json.loads(W.json)
    return jsonify(ret)

@app.route('/api/worker/<int:id>', methods=['DELETE'])
@auth.login_required
def del_mon_worker(id):
    W = Worker.query.get(id)
    if not W:
        abort(400)

    ret = W.delete()
    if ret:
        return (jsonify({'status': 'Worker deleted'}), 200)
    else:
        return (jsonify({'status': 'Failed to delete'}), 400)

@app.route('/api/worker')
@auth.login_required
def get_all_workers():
    data = {}
    workers = database.select_all(Worker)
    for worker in workers:
        data[worker.id] = json.loads(worker.json)
    return jsonify(data)

@app.route('/api/worker/<int:id>', methods=['POST'])
@auth.login_required
def post_mon_worker_data(id):
    W = Worker.query.get(id)
    if not W:
        abort(400)
    post_data = request.get_json(force=True)
    print(post_data)
    return jsonify(W.json)