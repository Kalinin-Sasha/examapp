import requests


def save_file(url, path):
    response = requests.get(url)
    with open(path, 'wb') as to_write:
        to_write.write(response.content)
