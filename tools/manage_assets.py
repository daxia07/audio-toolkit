# convert assets to music and playlist type
# for each album, if not found upload cover, upload songs, create entries and create playlist for the album
import os
from reformat import is_audio, is_image
from definitions import CWD, config
import contentful_management
import contentful
from loguru import logger


def run(f_path='output'):
    full_path = os.path.join(CWD, f_path)
    singers = [name for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]
    cma_client = contentful_management.Client(config['CONTENTFUL_TOKEN'])
    cda_client = contentful.Client(
        config['SPACE_ID'],
        config['CONTENTFUL_AT']
    )
    for singer in singers:
        albums = [name for name in os.listdir(os.path.join(full_path, singer)) if
                  os.path.isdir(os.path.join(full_path, singer, name))]
        for album in albums:
            # check if cover found in current assets

            # find the first image
            covers = [name for name in os.listdir(os.path.join(full_path, singer, album))
                      if is_image(os.path.join(full_path, singer, album, name))]
            if len(covers):
                # upload cover and attach cover url to each song in the album
                # check if exists
                pass
            # upload song and create song entry
            songs = [file for file in os.listdir(os.path.join(full_path, singer, album)) if is_audio(file)]
            for song in songs:
                existing_entries = cda_client.entries({'content_type': 'song',
                                                       'fields.album': album,
                                                       'fields.artist': singer,
                                                       'fields.title': song
                                                       })
                if len(existing_entries):
                    logger.warning(f'Found entry for album {album} by {singer}, will skip further actions!')
                    continue
                pass
            pass
        # create playlist


if __name__ == '__main__':
    run()
