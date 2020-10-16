"""The Simulator

"""

import requests
from flask.json import dumps
from gevent import sleep
from gevent import spawn_later
from math import asin
from math import cos
from math import pi
from math import sin
from math import sqrt
from random import uniform

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
        url = 'http://localhost:5000/update'

        data = {
            'drone': drone,
            'lat': latitude,
            'lon': longitude
        }

        #: IO Operation
        requests.post(url, json=dumps(data))
        sleep(5)


#: Spawn Simulators
def spawn():
    """Spawn simulators

    """

    jobs = list()
    for i in range(len(drones)):
        delay = i + 8
        jobs.append(spawn_later(delay, post_random_location, drones[i]))

    return jobs
