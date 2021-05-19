from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'


def read_storage_creds():
    with open('storage.json', 'rb') as f:
        content = f.read()
    return content


def save_creds_to_redis(r, data):
    pass


def get_creds():
    creds = client.Credentials.new_from_json(read_storage_creds())
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        store = file.Storage('storage.json')
        creds = tools.run_flow(flow, store)
        # save to redis
    return creds


def get_drive(creds):
    return discovery.build('drive', 'v3', http=creds.authorize(Http()))


def get_file_list():
    creds = get_creds()
    DRIVE = get_drive(creds)
    files = DRIVE.files().list().execute().get('files', [])
    for f in files:
        print(f['name'], f['mimeType'])


get_file_list()
