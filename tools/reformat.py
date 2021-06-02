import os
import re
import chinese_converter
import filetype
import shutil
from pathlib import Path
from definitions import CWD


def rename_folder(f_path='./music/周杰伦'):
    albums = [name for name in os.listdir(f_path) if os.path.isdir(os.path.join(f_path, name))]
    album_regex = re.compile(r'《(.*)》')
    for album in albums:
        try:
            album_name = album_regex.search(album).group(1).strip()
            print(f'{album} renaming to {album_name}')
            os.rename(os.path.join(f_path, album), os.path.join(f_path, album_name))
        except AttributeError:
            continue


def rename_files(f_path='./music', singer='周杰伦'):
    full_path = os.path.join(f_path, singer)
    albums = [name for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]
    # remove elements
    for album in albums:
        print(f"###album : {album}")
        songs = [name for name in os.listdir(os.path.join(full_path, album))
                 if not os.path.isdir(os.path.join(full_path, name))]
        for song in songs:
            original_name = song
            song = chinese_converter.to_simplified(song)
            song = format_name(singer, song)

            os.rename(os.path.join(full_path, album, original_name),
                      os.path.join(full_path, album, song))
            print(song)


def list_songs(f_path='./music', singer='周杰伦', include_cue=False):
    full_path = os.path.join(f_path, singer)
    albums = [name for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]
    # remove elements
    for album in albums:
        songs = [name for name in os.listdir(os.path.join(full_path, album))
                 if not os.path.isdir(os.path.join(full_path, name))]
        for song in songs:
            # only media file
            song_path = os.path.join(f_path, singer, album, song)
            if song.endswith('cue') and include_cue:
                yield song_path, singer, album, song
            else:
                if not is_audio(song_path):
                    continue
                yield song_path, singer, album, song


def add_meta_data():
    import mutagen
    for song_path, singer, album, song in list_songs(os.path.join(CWD, 'output')):
        print(song)
        file = mutagen.File(song_path)
        track_num = file.get('tracknumber', [''])[0]
        new_name = song.replace(f'{track_num.zfill(2)} - ', '')\
            .replace(f'{track_num.zfill(2)}.', '')
        os.rename(os.path.join(song_path),
                  os.path.join(CWD, 'output', singer, album, new_name))


def format_name(singer, name):
    elements = [f'{singer}-', f'{singer}.-.', f'{singer} - ', '.(flac)', '.专辑']
    for element in elements:
        name = name.replace(element, '')
    if name.startswith('['):
        filename, file_extension = os.path.splitext(name)
        name = filename.strip('[]') + file_extension
    return name.strip()


def is_audio(file_path):
    if os.path.basename(file_path).endswith('.ape'):
        return True
    return 'audio' in str(filetype.guess_mime(file_path))


def is_image(file_path):
    return 'image' in str(filetype.guess_mime(file_path))


def read_file_lines(file, codex='big5'):
    if codex.lower() == 'big5':
        codex_list = ['big5', 'gbk', 'utf-8']
    else:
        codex_list = [codex]
    lines = None
    for encoding in codex_list:
        f = open(file, encoding=encoding)
        try:
            lines = f.readlines()
            f.close()
        except UnicodeDecodeError:
            f.close()
            continue

    if lines is None:
        raise ValueError(f'Unable to decode file: {file}')

    return lines


def update_cue_file(song_path, song, singer, codex='Big5'):
    # use Big5 to encode Chinese chars
    album_folder = Path(song_path).parent.absolute()
    file_line_regex = re.compile(r'FILE "(.*)" WAVE')
    # get extension
    filename, file_extension = os.path.splitext(song)
    from glob import glob
    target_files = glob(os.path.join(album_folder, f'{filename.replace("-", "*")}*'))
    # filter media
    target_files = [file for file in target_files if is_audio(file)]
    if len(target_files) == 0:
        raise ValueError("No target files found")
    _, target_extension = os.path.splitext(os.path.basename(target_files[0]))
    lines = read_file_lines(song_path, codex)
    with open(os.path.join(album_folder, f'test_{song}'), 'w+') as writer:
        for line in lines:
            line = chinese_converter.to_simplified(line)
            if line.startswith('FILE'):
                print(line)
                file_line = file_line_regex.search(line).group(1).strip()
                file_line = format_name(singer, file_line)
                if 'CDImage' in file_line:
                    file_line = Path(song_path).parent.name + '.' + file_extension
                line = 'FILE "' + file_line + '" WAVE\n'
            writer.write(line)
    shutil.move(os.path.join(album_folder, f'test_{song}'), song_path)


def convert_cue_files():
    # re-create cue file
    for song_path, singer, album, song in list_songs(include_cue=True):
        if song.endswith('.cue'):
            # modify cue file
            print(song)
            update_cue_file(song_path, song, singer)
            # should be the only file to decode


def rm_tree_if_exist(f_path):
    if Path(f_path).is_dir():
        # clear up files
        shutil.rmtree(f_path)


def split_music(f_path='./music', singer='周杰伦', output='./output'):
    from deflacue.deflacue import Deflacue
    from deflacue.exceptions import ParserError
    full_path = os.path.join(f_path, singer)
    albums = [name for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]
    full_path_abs = Path(full_path).absolute()
    des_abs_path = Path(output).absolute()
    tmp_folder = os.path.join(des_abs_path, 'temp')
    for album in albums:
        src_abs_path = os.path.join(full_path_abs, album)
        des_folder = os.path.join(des_abs_path, singer, album)
        # make temp folder and copy to des
        # if no cue found, copy files and continue
        cue_files = [x for x in os.listdir(src_abs_path) if x.endswith('.cue')]
        if len(cue_files) == 0:
            print(f'No cue file found for album {album}')
            rm_tree_if_exist(des_folder)
            shutil.copytree(src_abs_path, des_folder)
            continue
        rm_tree_if_exist(tmp_folder)
        os.mkdir(tmp_folder)
        try:
            dfc = Deflacue(src_abs_path, dest_path=tmp_folder)
            dfc.do()
            # loop over tmp folder to copy files
            # mv files to output/singer/album
            Path(des_folder).mkdir(parents=True, exist_ok=True)
            for subdir, dirs, files in os.walk(tmp_folder):
                for file in files:
                    # os.path.join(subdir, file)
                    file_path = os.path.join(subdir, file)
                    if is_audio(file_path):
                        shutil.copy2(file_path, des_folder)

            # copy and rename the first image as album
            for src_file in os.listdir(src_abs_path):
                if is_image(src_file):
                    # get extension
                    _, file_extension = os.path.splitext(src_file)
                    shutil.copy2(os.path.join(src_abs_path, src_file),
                                 os.path.join(des_folder, f'{album}{file_extension}'))
                    break

        except ParserError as e:
            print(e)
            # copy all files to des folder
            shutil.copytree(src_abs_path, os.path.join(des_abs_path, singer, album))
            continue
        finally:
            rm_tree_if_exist(tmp_folder)


if __name__ == '__main__':
    # rename_folder()
    # rename_files()
    # convert_cue_files()
    # split_music()
    add_meta_data()
    pass
