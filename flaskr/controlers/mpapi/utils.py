from ..mpapi import TEMP_FILE_PATH, SERVER_URL, MEDIA_UP_URL
import requests, time, os, json


def download(url, name):
    r = requests.get(url)
    with open('{}/img-{}.jpg'.format(TEMP_FILE_PATH, time.strftime("%Y_%m_%d%H_%M_%S", time.localtime())), 'wb') as fd:
        fd.write(r.content)
    if os.path.getsize(fd.name) >= 1048576:
        return ''
    return os.path.basename(fd.name)


def upload(mediaType, name, token=None):
    url = SERVER_URL + MEDIA_UP_URL % (token, mediaType)
    files = {'media': open('{}/{}'.format(TEMP_FILE_PATH, name), 'rb')}
    r = requests.post(url, files=files)
    parse_json = json.loads(r.text)
    return parse_json['media_id']

def delete_temp_file():
    for name in os.listdir(TEMP_FILE_PATH):
        path = '%s%s' % (TEMP_FILE_PATH, name)
        if os.path.exists(path):
            os.remove(path)

