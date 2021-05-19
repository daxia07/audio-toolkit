import json

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client

SCOPES = 'https://www.googleapis.com/auth/drive'
DEFAULT_COVER = 'https://images.unsplash.com/photo-1514924527133-371124f6f5e3?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=2534&q=80'


def read_storage_creds():
    with open('storage.json', 'rb') as f:
        content = f.read()
    return content


def get_creds_from_redis(r):
    return r.get('creds')


def save_creds_to_redis(r, data):
    r.set('creds', data)


def get_creds_instance(r):
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
    creds = get_creds_instance(r)
    DRIVE = get_drive(creds)
    files = DRIVE.files().list().execute().get('files', [])
    for f in files:
        print(f['name'], f['mimeType'])
    return files


def find_songs(r):
    creds = get_creds_instance(r)
    drive_service = get_drive(creds)
    data = []
    singer_folder = drive_service.files() \
        .list(q="(mimeType='application/vnd.google-apps.folder' and name='singers')",
              spaces='drive',
              fields='files(id, name)')\
        .execute()
    for singer_folder in singer_folder.get('files', []):
        # Identify singers folder and keep searching
        singers = drive_service.files() \
            .list(q=f"(mimeType='application/vnd.google-apps.folder' and '{singer_folder.get('id')}' in parents)",
                  spaces='drive',
                  fields='files(id, name)') \
            .execute()
        for singer in singers.get('files', []):
            singer_name = singer.get('name')
            albums = drive_service.files() \
                .list(q=f"(mimeType='application/vnd.google-apps.folder' and '{singer.get('id')}' in parents)",
                      spaces='drive',
                      fields='files(id, name)') \
                .execute()
            for album in albums.get('files', []):
                album_name = album.get('name')
                # find cover
                covers = drive_service.files() \
                    .list(q=f"(mimeType contains 'image' and '{album.get('id')}' in parents)",
                          spaces='drive',
                          fields='files(id, name)') \
                    .execute()
                cover = covers.get('files', [])
                cover_url = DEFAULT_COVER if len(cover) == 0 else f"https://docs.google.com/uc?export=download&id={cover[0].get('id')}"
                # get music
                songs = drive_service.files() \
                    .list(q=f"(mimeType contains 'audio' and '{album.get('id')}' in parents)",
                          spaces='drive',
                          fields='files(id, name)') \
                    .execute()
                for song in songs.get('files', []):
                    song_id = song.get('id')
                    song_name = song.get('name')
                    song_url = f"https://docs.google.com/uc?export=download&id={song_id}"
                    data.append({
                        "singer": singer_name,
                        "album": album_name,
                        "name": song_name,
                        "musicSrc": song_url,
                        "cover": cover_url
                    })
    r.set("driveMusicList", json.dumps({"data": data}))
    return data


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
    # get_file_list(r)
    # creds = get_creds_instance(r)
    # drive_service = get_drive(creds)
    find_songs(r)
    print('OK')
