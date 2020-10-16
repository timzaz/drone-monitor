# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license
# information.
# -----------------------------------------------------------------------------

from flask import Flask
from flask import jsonify
from flask import render_template
from flask_socketio import SocketIO

app = Flask(__name__)
async_mode = None

store = dict()
socketio = SocketIO(app=app, async_mode=async_mode)


@app.route('/')
def index():
    """Renders the index page that displays monitoring visuals.

    """

    return render_template('index.jinja2')


@app.route('/update', methods=('POST',))
def drone_update():
    """Drones post updates to the server. The server emits an event so the
    client can update the user interface in realtime.

    """

    socketio.emit('drone_update', {
        'drone': 'cscan15',
        'highlight': False,
        'speed': 40,
    }, namespace='/')

    return jsonify(), 204


@socketio.on('connect')
def on_connect():
    print('Socket is connected.')


@socketio.on('disconnect')
def on_disconnect():
    print('Socket is disconnected.')
