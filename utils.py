# python utilities
import json
import os
import re


def save_json_to_file(data, file='data.json', current_working_dir=os.getcwd()):
    try:
        with open(file, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        create_path_to_file(file, current_working_dir)
        # target directory should now exist, try again
        save_json_to_file(data, file)


def read_json_from_file(file_name='data.json'):
    with open(file_name, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data


def write_to_file(data, file='data.txt', current_working_dir=os.getcwd()):
    try:
        with open(file, 'w', encoding='utf8') as f:
            f.write(data)
    except FileNotFoundError:
        create_path_to_file(file, current_working_dir)


def read_from_file(file_name='data.txt'):
    with open(file_name, 'r', encoding='utf8') as f:
        data = f.read()
    return data


def create_path_to_file(file_path, working_dir=os.getcwd()):
    # create the path if it doesn't exist
    match = re.search(r'(.*)\/(.*\.[A-z]+$)', file_path)
    folder_path = match.group(1)

    folder_paths = re.split(r'\/|\\', folder_path)

    # recursively create the path
    for new_folder in folder_paths:
        working_dir = os.path.join(working_dir, new_folder)
        os.mkdir(working_dir)


def get_12hr_time_format_for_os(os_name=None):
    if os_name == 'Windows_NT':
        return "%#I:%M %p"
    else:
        return "%-I:%M %p"
