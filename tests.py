import pytest
from app import app
from app import socketio
from app import store
from flask.json import dumps
from random import uniform
from simulator import min_latitude
from simulator import min_longitude
from simulator import max_latitude
from simulator import max_longitude
from time import sleep


@pytest.mark.parametrize(
    'url, method',
    [
        ('/', 'post'),
        ('/update', 'get'),
        ('/fake-route', 'get'),
    ])
def test_error_handler_handles_unknown_routes(url, method):
    client = app.test_client()

    response = getattr(client, method)(url)
    assert response.status_code == 406


def test_index_route_success():
    client = app.test_client()
    url = '/'

    response = client.get(url)
    assert response.status_code == 200


def test_update_route_returns_no_content():
    client = app.test_client()

    url = '/update'
    latitude = round(uniform(min_latitude, max_latitude), 6)
    longitude = round(uniform(min_longitude, max_longitude), 6)

    data = {
        'drone': 'carbuncle',
        'lat': latitude,
        'lon': longitude
    }
    response = client.post(url, json=dumps(data))

    assert response.get_data() == b''
    assert response.status_code == 204


def test_update_highlights_on_ten_second_stagnation():
    client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    assert socket_client.is_connected() is True

    url = '/update'
    latitude = round(uniform(min_latitude, max_latitude), 6)
    longitude = round(uniform(min_longitude, max_longitude), 6)

    data = {
        'drone': 'carbuncle',
        'lat': latitude,
        'lon': longitude
    }

    client.post(url, json=dumps(data))
    r1 = socket_client.get_received()

    sleep(11)

    client.post(url, json=dumps(data))
    r2 = socket_client.get_received()

    assert r1[0]['args'][0]['drone'] == 'carbuncle'
    assert r2[0]['args'][0]['highlight'] is True
    assert r2[0]['args'][0]['speed'] == 0

    assert r1[0]['name'] == 'drone_update'
    assert r2[0]['name'] == 'drone_update'

    assert store.get('carbuncle', None) is not None


def test_update_route_signals_client():
    client = app.test_client()

    socket_client = socketio.test_client(app)
    socket_client.get_received()

    assert socket_client.is_connected() is True

    url = '/update'
    latitude = round(uniform(min_latitude, max_latitude), 6)
    longitude = round(uniform(min_longitude, max_longitude), 6)

    data = {
        'drone': 'carbuncle',
        'lat': latitude,
        'lon': longitude
    }

    client.post(url, json=dumps(data))

    received = socket_client.get_received()

    assert received[0]['args'][0]['drone'] == 'carbuncle'
    assert received[0]['args'][0]['highlight'] is False
    assert received[0]['args'][0]['speed'] >= 0
    assert received[0]['name'] == 'drone_update'
    assert store.get('carbuncle', None) is not None
