import json
import os.path
import shutil
import subprocess
from datetime import datetime

import exifread

source_folder = 'D:/Photos'
target_folder = 'D:/Photos Organized'

month_to_str = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}


def get_data_taken(path):
    with open(path, 'rb') as fh:
        try:
            tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            dt = tags["EXIF DateTimeOriginal"]
            return datetime.strptime(str(dt), '%Y:%m:%d %H:%M:%S').timestamp()
        except Exception as e:
            return 0


def get_data_taken_video(file_path):
    try:
        command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
        result = subprocess.run(command, capture_output=True, text=True)
        result.check_returncode()  # Check if the subprocess ran successfully
        data = json.loads(result.stdout)

        if 'format' in data and 'tags' in data['format'] and 'creation_time' in data['format']['tags']:
            # Parse the creation time to a datetime object
            creation_time = datetime.strptime(data['format']['tags']['creation_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
            # Check if the creation time is greater than or equal to the minimum allowed timestamp value
            min_timestamp = datetime(1970, 1, 1, 1, 0, 0)
            if creation_time >= min_timestamp:
                # Convert to a timestamp and return
                return creation_time.timestamp()

    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"An error occurred while processing the video: {e}")

    return None


for path, subdirs, files in os.walk(source_folder):
    for name in files:
        file = os.path.join(path, name)
        file_extension = os.path.splitext(file)[1].lower()

        if file_extension in ['.mp4', '.mov']:
            date_taken = get_data_taken_video(file)
        else:
            date_taken = get_data_taken(file)

        t1 = os.path.getatime(file)
        t2 = os.path.getmtime(file)
        t3 = os.path.getctime(file)

        if date_taken:
            creation_timestamp = min(t1, t2, t3, date_taken)
        else:
            creation_timestamp = min(t1, t2, t3)

        creation_time = datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        year = datetime.fromtimestamp(creation_timestamp).strftime('%Y')
        month = datetime.fromtimestamp(creation_timestamp).strftime('%m')
        day = datetime.fromtimestamp(creation_timestamp).strftime('%d')

        move_to = f'{target_folder}/{year}/{year}_{month}_{month_to_str[month]}/{day}'

        if not os.path.exists(move_to):
            print(f'Creating directory {move_to}')
            os.makedirs(move_to)

        # while True:
        #     os.path.isfile(path)
        target_path = f'{move_to}/{name}'

        if os.path.isfile(target_path):
            counter = 0
            name, ext = os.path.splitext(name)
            while os.path.isfile(target_path):
                counter += 1
                target_path = f'{move_to}/{name}_{counter}{ext}'
                print('New target path', target_path)

        shutil.move(file, target_path)
