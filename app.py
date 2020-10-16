"""The Flask Application

"""

from gevent import monkey
monkey.patch_all()  # noqa

import requests
from time import time
from flask import Flask
from flask import jsonify
from flask import render_template
from flask.globals import request
from flask.json import dumps
from flask.json import loads
from flask_socketio import SocketIO
from gevent import sleep
from gevent import spawn_later
from math import asin
from math import cos
from math import pi
from math import sin
from math import sqrt
from random import uniform

app = Flask(__name__)
async_mode = None

drones = [
    'sle000',
    'sle001',
    'sle002',
    'sle003',
    'sle004',
    'sle005',
    'sle006',
    'sle007',
    'sle008',
    'sle009'
]

#: Estimated bounding box for Sierra Leone
min_latitude = 6.929863
min_longitude = -13.316667
max_latitude = 10.006289
max_longitude = -10.276414

store = dict()
socketio = SocketIO(app=app, async_mode=async_mode)


def distance(lat1, lon1, lat2, lon2):
    """Calculates the distance between two coordinates.

    """

    #: R = 3958.8  #: For Miles
    R = 6371.0710  #: For KM

    radLat1 = pi * lat1 / 180
    radLat2 = pi * lat2 / 180

    diffLat = radLat2 - radLat1
    diffLon = lon2 - lon1

    diffLon = pi * diffLon / 180

    diffLatSquare = sin(diffLat / 2) * sin(diffLat / 2)
    diffLonSquare = sin(diffLon / 2) * sin(diffLon / 2)

    return 2 * R * asin(
        sqrt(
            diffLatSquare + cos(radLat1) * cos(radLat2) * diffLonSquare
        )
    )


def post_random_location(drone):
    """Receives a drone and posts random location every few seconds.

    """

    while True:
        #: Generate lat/lon coordinates and round to 6 decimal places
        latitude = round(uniform(min_latitude, max_latitude), 6)
        longitude = round(uniform(min_longitude, max_longitude), 6)
        url = 'http://localhost:9000/update'

        data = {
            'drone': drone,
            'lat': latitude,
            'lon': longitude
        }

        #: IO Operation
        requests.post(url, json=dumps(data))
        sleep(5)


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
        distance_travelled = distance(
            latitude,
            longitude,
            last_update.get('lat'),
            last_update.get('lon')
        )  # calculate
        elapsed = posted - last_update.get('time')

        if distance_travelled > 1 and elapsed > 10:
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


@socketio.on('connect')
def on_connect():
    print('Socket is connected.')


@socketio.on('disconnect')
def on_disconnect():
    print('Socket is disconnected.')


#: Spawn Simulators
jobs = list()
for i in range(len(drones)):
    delay = i + 8
    jobs.append(spawn_later(delay, post_random_location, drones[i]))
