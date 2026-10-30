"""API tests use a fresh collection in a disposable MongoDB database."""

import json
from uuid import uuid4

import pytest

from backend import app as flask_app
from backend import routes


@pytest.fixture(scope='session')
def test_database():
    database = routes.client['songs_test_' + uuid4().hex]
    database.command('ping')
    yield database
    routes.client.drop_database(database.name)


@pytest.fixture(autouse=True)
def database(test_database, monkeypatch):
    monkeypatch.setattr(routes, 'db', test_database)
    with open(routes.json_url) as seed_file:
        test_database.songs.insert_many(json.load(seed_file))
    yield test_database
    test_database.songs.delete_many({})


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setitem(flask_app.config, 'TESTING', True)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def song():
    return {'id': 323, 'title': 'New song', 'lyrics': 'New lyrics'}
