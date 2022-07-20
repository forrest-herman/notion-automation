# python utilities
import json


def save_json_to_file(data, file_name='data.json'):
    with open(file_name, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_to_file(data, file_name='data.txt'):
    with open(file_name, 'w', encoding='utf8') as f:
        f.write(data)
