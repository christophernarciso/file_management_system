import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ? supported directories
user_env = os.getenv('username')
source_dir = f'/Users/{user_env}/Downloads'
video_dir = f'/Users/{user_env}/Videos'
picture_dir = f'/Users/{user_env}/Pictures'
music_dir = f'/Users/{user_env}/Music'
document_dir = f'/Users/{user_env}/Documents'

# ? supported image types
image_extensions = ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi', '.png', '.gif', '.webp', '.tiff', '.tif', '.psd',
                    '.raw', '.arw', '.cr2', '.nrw', '.k25', '.bmp', '.dib', '.heif', '.heic', '.ind', '.indd', '.indt',
                    '.jp2', '.j2k', '.jpf', '.jpf', '.jpx', '.jpm', '.mj2', '.svg', '.svgz', '.ai', '.eps', '.ico']
# ? supported video types
video_extensions = ['.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.ogg', '.mp4', '.mp4v', '.m4v', '.avi', '.wmv',
                    '.mov', '.qt', '.flv', '.swf', '.avchd', '.mkv']
# ? supported audio types
audio_extensions = ['.m4a', '.flac', 'mp3', '.wav', '.wma', '.aac']
# ? supported document types
document_extensions = ['.doc', '.docx', '.odt', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx']
# ? supported installation types
installer_extensions = ['.msi', '.exe']


class MoveHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with os.scandir(source_dir) as entries:
            # Loop through the entries and prepare their destination
            for entry in entries:
                name = entry.name
                dest = None
                ext = os.path.splitext(name)[-1].lower()
                logging.info(f'Scanning: {name} Extension: {ext}')
                # Check file extensions and set the proper destination
                if ext in audio_extensions:
                    logging.info(f'Found audio: {name}')
                    dest = music_dir
                elif ext in video_extensions:
                    logging.info(f'Found video: {name}')
                    dest = video_dir
                elif ext in image_extensions:
                    logging.info(f'Found image: {name}')
                    dest = picture_dir
                elif ext in document_extensions:
                    logging.info(f'Found document: {name}')
                    dest = document_dir
                elif ext in installer_extensions:
                    logging.info(f'Found installer: {name}')
                    dest = f'{source_dir}/Installers'
                    if not os.path.exists(dest):
                        os.mkdir(dest)

                # If a destination was set then we move the file.
                if dest is not None:
                    MoveHandler.move_file(dest, entry, name)

    @staticmethod
    def move_file(destination, entry, name):
        existing_file = os.path.exists(f'{destination}/{name}')
        file = entry
        if existing_file:
            logging.warning(f'File {name} already exist in destination {destination}.')
            new_name = MoveHandler.rename_duplicate(destination, name)
            new_path = f'{source_dir}/{new_name}'
            logging.info('Renaming file using os.rename')
            try:
                os.rename(file, new_path)
            except PermissionError:
                logging.warning('Entry renaming encountered permission error. Failed to move file.')
            # We renamed the file but still holds reference to old name and path...don't know
            file = new_path

        logging.info(f'Moving file to {destination}')
        try:
            shutil.move(file, destination)
        except FileExistsError:
            logging.warning(f'Entry {file} exists in the following destination {destination}. Failed to move file.')
        except FileNotFoundError:
            logging.warning(f'Failed to find {entry}. Failed to move file.')

    @staticmethod
    def rename_duplicate(destination, name):
        # get the filename split from the .ext
        name_splitter = name.split('.')
        file_name = name_splitter[0]
        ext = name_splitter[1]
        inc = 1

        while True:
            exists = os.path.exists(f'{destination}/{file_name}({inc}).{ext}')
            # Keep looping until we get a filename pattern that does not exist.
            if not exists:
                renamed = f'{file_name}({inc}).{ext}'
                logging.info(f'Renaming duplicate to: {renamed}')
                break
            inc += 1

        return renamed


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename=f'{document_dir}/filewatcher.log',
                        format='[%(levelname)s][%(asctime)s] - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoveHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
