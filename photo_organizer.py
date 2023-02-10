import os.path
import shutil
from datetime import datetime

import exifread

source_folder = 'D:/Photos'
target_folder = 'D:/photos_organized_2'

month_to_str = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}


def get_data_taken(path):
    with open(path, 'rb') as fh:
        try:
            tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            dt = tags["EXIF DateTimeOriginal"]
            return datetime.strptime(str(dt), '%Y:%m:%d %H:%M:%S').timestamp()
        except Exception as e:
            return 0


for path, subdirs, files in os.walk(source_folder):
    for name in files:
        file = os.path.join(path, name)

        t1 = os.path.getatime(file)
        t2 = os.path.getmtime(file)
        t3 = os.path.getctime(file)
        date_taken = get_data_taken(file)

        if date_taken:
            creation_timestamp = min(t1, t2, t3, date_taken)
        else:
            creation_timestamp = min(t1, t2, t3)

        creation_time = datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        year = datetime.fromtimestamp(creation_timestamp).strftime('%Y')
        month = datetime.fromtimestamp(creation_timestamp).strftime('%m')

        move_to = f'{target_folder}/{year}/{year}_{month}_{month_to_str[month]}'

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
