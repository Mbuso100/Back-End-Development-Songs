# Back-End-Development-Songs

Flask and PyMongo implementation of the IBM **Creating Get Songs Service with
Flask** lab.

## Run locally

Install `requirements.txt` with Python 3.9 and start a dedicated MongoDB server.
In this prepared cloud environment:

```bash
cd /workspace/Back-End-Development-Songs
source /workspace/.venvs/songs/bin/activate
export MONGODB_SERVICE=127.0.0.1:27017
FLASK_APP=app flask run --host 127.0.0.1 --port 5000 --no-reload
```

The starter application drops and reseeds `songs.songs` with 20 songs whenever
it is imported. Use a disposable local database, never a shared database. Keep
`MONGODB_USERNAME` and `MONGODB_PASSWORD` unset for the local unauthenticated
development container. For authenticated lab MongoDB, supply those variables
securely; the starter logs its connection URL, so do not share logs containing
credentials.

## API contract

| Method | Path | Success response |
| --- | --- | --- |
| GET | `/health` | 200, `{"status":"OK"}` |
| GET | `/count` | 200, `{"count":20}` initially |
| GET | `/song` | 200, `{"songs":[...]}` |
| GET | `/song/<int:id>` | 200, song document |
| POST | `/song` | 201, `{"inserted id":{"$oid":"..."}}` |
| PUT | `/song/<int:id>` | 201, updated song document |
| DELETE | `/song/<int:id>` | 204, empty body |

Song documents contain `id`, `title`, `lyrics`, and MongoDB `_id` serialized as
`{"$oid":"..."}`. POST accepts a JSON song document. Duplicate IDs return 302
with `{"Message":"song with id 323 already present"}` (using the supplied ID).
GET of a missing ID returns 404 with `{"message":"song with id not found"}`.
PUT and DELETE of a missing ID return 404 with `{"message":"song not found"}`.
PUT applies the supplied fields with `$set`; an unchanged document returns 200
with `{"message":"song found, but nothing updated"}`.

The lab's summary table says PUT returns 200, but its detailed Exercise 5 example
shows 201 when a document changes. This implementation follows that detailed
example and returns 200 for an unchanged document. POST also follows the detailed
inserted-ID response rather than the summary table's song-resource description.

## Automated tests

With MongoDB running, use the same virtual environment and service variable:

```bash
MONGODB_SERVICE=127.0.0.1:27017 python -m pytest -p no:cacheprovider
```

Tests use real MongoDB and a temporary database with fresh seed data per test;
the temporary database is removed after the suite. Importing the starter app
still reseeds its development collection before the test fixtures run.

## Coursera submission

- Keep the repository public and named `Back-End-Development-Songs`, created
  using the course template. Submit the public README URL for AI grading or the
  repository URL for peer grading.
- Push the implementation branch, open a pull request into `main`, merge it,
  and delete the branch after merging, as instructed by the lab.
- For AI grading, submit actual curl output in text files named
  `songs-ex1-health-curl`, `songs-ex2-get-song-curl`,
  `songs-ex5-put-song-passing`, and `songs-ex6-delete-song-passing`.
- For peer grading, capture the corresponding successful curl responses as
  `.jpg` or `.png` screenshots. The lab spells the PUT screenshot filename
  `songs-ex5--put-song-passing` (two hyphens); use the current submission form's
  requested spelling. Upload the files through Coursera.

Publishing this cloud environment does not push code or submit Coursera work.
