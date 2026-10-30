import json

import pytest
from bson import ObjectId


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.is_json
    assert res.get_json() == {"status": "OK"}


def test_health_rejects_post(client):
    res = client.post("/health")
    assert res.status_code == 405


def test_count(client):
    res = client.get('/count')
    assert res.status_code == 200
    assert res.get_json() == {'count': 20}


def test_list_songs(client, database):
    res = client.get('/song')
    assert res.status_code == 200
    songs = res.get_json()['songs']
    assert len(songs) == 20
    assert {song['id'] for song in songs} == set(range(1, 21))
    for song in songs:
        stored = database.songs.find_one({'id': song['id']})
        assert song == {
            '_id': {'$oid': str(stored['_id'])},
            'id': stored['id'],
            'title': stored['title'],
            'lyrics': stored['lyrics'],
        }


def test_get_song_by_integer_id(client, database):
    res = client.get('/song/1')
    assert res.status_code == 200
    stored = database.songs.find_one({'id': 1})
    assert res.get_json() == {
        '_id': {'$oid': str(stored['_id'])},
        'id': 1, 'title': stored['title'], 'lyrics': stored['lyrics'],
    }


def test_get_missing_song(client):
    res = client.get('/song/999')
    assert res.status_code == 404
    assert res.get_json() == {'message': 'song with id not found'}


def test_create_song(client, database, song):
    res = client.post('/song', json=song)
    assert res.status_code == 201
    inserted_id = res.get_json()['inserted id']
    assert ObjectId.is_valid(inserted_id['$oid'])
    assert database.songs.find_one({'_id': ObjectId(inserted_id['$oid'])}) == {
        '_id': ObjectId(inserted_id['$oid']), **song,
    }
    assert client.get('/count').get_json() == {'count': 21}
    assert client.get('/song/323').get_json() == {'_id': inserted_id, **song}


def test_duplicate_song(client, database, song):
    assert client.post('/song', json=song).status_code == 201
    res = client.post('/song', json={**song, 'title': 'Do not overwrite'})
    assert res.status_code == 302
    assert res.get_json() == {'Message': 'song with id 323 already present'}
    assert database.songs.count_documents({'id': 323}) == 1
    assert database.songs.find_one({'id': 323})['title'] == song['title']


def test_update_song(client, database):
    original_id = database.songs.find_one({'id': 1})['_id']
    changes = {'title': 'yay song', 'lyrics': 'yay hey yay yay'}
    res = client.put('/song/1', json=changes)
    assert res.status_code == 201  # Detailed Exercise 5 curl example.
    expected = {'_id': {'$oid': str(original_id)}, 'id': 1, **changes}
    assert res.get_json() == expected
    assert client.get('/song/1').get_json() == expected
    assert database.songs.count_documents({}) == 20


def test_update_unchanged_song(client):
    changes = {'title': 'yay song', 'lyrics': 'yay hey yay yay'}
    assert client.put('/song/1', json=changes).status_code == 201
    res = client.put('/song/1', json=changes)
    assert res.status_code == 200
    assert res.get_json() == {'message': 'song found, but nothing updated'}


def test_partial_update_preserves_other_fields(client):
    original = client.get('/song/1').get_json()
    res = client.put('/song/1', json={'title': 'Changed title'})
    assert res.status_code == 201
    assert res.get_json() == {**original, 'title': 'Changed title'}


def test_update_missing_song(client, database):
    res = client.put('/song/999', json={'title': 'Missing song'})
    assert res.status_code == 404
    assert res.get_json() == {'message': 'song not found'}
    assert database.songs.find_one({'id': 999}) is None


def test_delete_song(client, database):
    res = client.delete('/song/14')
    assert res.status_code == 204
    assert res.data == b''
    assert database.songs.find_one({'id': 14}) is None
    assert client.get('/count').get_json() == {'count': 19}
    assert client.get('/song/14').status_code == 404
    repeated = client.delete('/song/14')
    assert repeated.status_code == 404
    assert repeated.get_json() == {'message': 'song not found'}


def test_delete_missing_song(client, database):
    res = client.delete('/song/999')
    assert res.status_code == 404
    assert res.get_json() == {'message': 'song not found'}
    assert database.songs.count_documents({}) == 20


def test_empty_collection(client, database):
    database.songs.delete_many({})
    assert client.get('/count').get_json() == {'count': 0}
    res = client.get('/song')
    assert res.status_code == 200
    assert res.get_json() == {'songs': []}


@pytest.mark.parametrize('method,path', [
    ('post', '/song'), ('put', '/song/1'),
])
@pytest.mark.parametrize('payload', [None, [], 'invalid'])
def test_non_object_body(client, database, method, path, payload):
    res = getattr(client, method)(path, data=json.dumps(payload),
                                 content_type='application/json')
    assert res.status_code == 400
    assert database.songs.count_documents({}) == 20


def test_create_without_id(client, database):
    res = client.post('/song', json={'title': 'Missing ID'})
    assert res.status_code == 400
    assert database.songs.count_documents({}) == 20


@pytest.mark.parametrize('method,path', [('post', '/song'), ('put', '/song/1')])
def test_malformed_json(client, method, path):
    res = getattr(client, method)(path, data='{', content_type='application/json')
    assert res.status_code == 400
