"""The Flask Application

"""

from gevent import monkey
monkey.patch_all()  # noqa

from time import time
from flask import Flask
from flask import jsonify
from flask import render_template
from flask.globals import request
from flask.json import loads
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

from simulator import distance
from simulator import spawn

app = Flask(__name__)
async_mode = None

store = dict()
socketio = SocketIO(app=app, async_mode=async_mode)


@app.route('/update', methods=('POST',))
def drone_update():
    """Drones post updates to the server. The server emits an event so the
    client can update the user interface in realtime.

    """

    data = loads(request.get_json(silent=True))

    drone = data.get('drone')
    latitude = data.get('lat')
    longitude = data.get('lon')
    posted = time()

    #: Initialise defaults
    highlight = False
    speed = 0

    last_update = store.get(drone, None)
    if last_update:
        #: Kilometers
        distance_travelled = distance(
            latitude,
            longitude,
            last_update.get('lat'),
            last_update.get('lon')
        )
        elapsed = posted - last_update.get('time')

        if (distance_travelled * 1000) <= 1 and elapsed > 10:
            highlight = True
        speed = round(distance_travelled / elapsed)

    #: Notify client
    socketio.emit('drone_update', {
        'drone': drone,
        'highlight': highlight,
        'speed': speed,
    }, namespace='/')

    #: Cache memory
    store[drone] = {
        'lat': latitude,
        'lon': longitude,
        'time': posted
    }

    return jsonify(), 204


@app.route('/')
def index():
    """Renders the index page that displays monitoring visuals.

    """

    return render_template('index.jinja2')


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Generic http exception handler.

    """

    return jsonify(), 406


#: Finally, spawn
spawn()
