import logging
import json
import azure.functions as func
import os
from redis import Redis
from .google_driver import find_songs


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    r = Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], password=os.environ["REDIS_PASS"])
    # if cached, fetch from redis and then update
    # else, scan and then send
    cached = req.params.get('cached', False)
    if cached:
        # cached_songs = json.loads(r.get('driveMusicList'))
        return func.HttpResponse(
            r.get('driveMusicList'),
            status_code=200,
            mimetype="application/json"
        )
    data = find_songs(r)
    if data:
        return func.HttpResponse(
            json.dumps({"data": data}),
            status_code=200,
            mimetype="application/json"
        )
    else:
        return func.HttpResponse(
            json.dumps({"data": f"No token found"}),
            status_code=400,
            mimetype="application/json",
        )
