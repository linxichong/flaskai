import os
import requests
requests.packages.urllib3.disable_warnings()
requests = requests.session()
requests.verify = False

SERVER_URL = 'https://api.weixin.qq.com'
GET_TOKEN_URL = '/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
MEDIA_UP_URL = '/cgi-bin/media/upload?access_token=%s&type=%s'

TEMP_FILE_PATH = 'flaskr/static/temp/'
INSTANCE_PATH = 'instance/'

try:
    os.makedirs(TEMP_FILE_PATH)
except OSError:
    pass
