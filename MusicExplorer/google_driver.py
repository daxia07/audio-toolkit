from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client

SCOPES = 'https://www.googleapis.com/auth/drive'


def read_storage_creds():
    with open('storage.json', 'rb') as f:
        content = f.read()
    return content


def get_creds_from_redis(r):
    return r.get('creds')


def save_creds_to_redis(r, data):
    r.set('creds', data)


def get_creds(r):
    creds = client.Credentials.new_from_json(get_creds_from_redis(r))
    if not creds or creds.invalid:
        raise ValueError("No valid credentials found to grant access")
        # flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        # store = file.Storage('storage.json')
        # creds = tools.run_flow(flow, store)
    return creds


def get_drive(creds):
    return discovery.build('drive', 'v3', http=creds.authorize(Http()))


def get_file_list(r):
    creds = get_creds(r)
    DRIVE = get_drive(creds)
    files = DRIVE.files().list().execute().get('files', [])
    for f in files:
        print(f['name'], f['mimeType'])


def init_creds():
    import json
    import redis
    with open('../local.settings.json') as f:
        settings = json.load(f)['Values']
    r = redis.Redis(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"], password=settings["REDIS_PASS"])
    # secrets = read_storage_creds()
    # save_creds_to_redis(r, secrets)
    return r


if __name__ == '__main__':
    r = init_creds()
    get_file_list(r)
    print('OK')
