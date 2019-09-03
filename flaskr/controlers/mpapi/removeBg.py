from enum import Enum
import json
import requests
from flaskr.base import CoreMixin
from ..mpapi import TEMP_FILE_PATH
import threading
import time


class BgColor():
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (67, 142, 219)


class RemoveBackgroud(CoreMixin):
    def __init__(self, core):
        super().__init__(core)
        self.api_key = self.core.config.get('REMOVEBG_API_KEY')
        self.api_url = self.core.config.get('REMOVEBG_API_URL')
        self.task_ids = {}
        self.invalid_keys = []

    '''
    size  (regular = 0.25 MP, hd = 4 MP, 4k = up to 10 MP)
    '''

    def do_remove(self, file_name, size='regular'):
        import uuid
        taskid = uuid.uuid1().hex

        t1 = threading.Thread(target=run_removebg_bythread,
                              args=(self, file_name, size, taskid))
        t1.start()
        # response = requests.post(
        #     api_url,
        #     files={'image_file': img_file},
        #     data={'size': size},
        #     headers={'X-Api-Key': api_key})

        # new_img_path = name + "_no_bg.png"

        # if response.status_code == requests.codes.ok:
        #     with open(new_img_path, 'wb') as removed_bg_file:
        #         removed_bg_file.write(response.content)
        # else:
        #     raise Exception()

        return taskid

    def get_result_bytaskid(self, taskid):
        img_name = None
        splits = taskid.split('/')
        taskid = splits[0]
        color = splits[1] if len(splits) > 1 else None
        try:
            img_name = self.task_ids.pop(taskid)
            if img_name != 'error':
                if color:
                    add_bgcolor(img_name, getattr(BgColor, color.upper()))
                else:
                    add_bgcolor(img_name)
        except Exception as e:
            pass
        return img_name


def add_bgcolor(file_name, bgColor=BgColor.WHITE):
    from PIL import Image
    img = Image.open(TEMP_FILE_PATH + file_name)
    x, y = img.size
    try:
        p = Image.new('RGBA', img.size, bgColor)
        p.paste(img, (0, 0, x, y), img)
        p.save(TEMP_FILE_PATH + file_name)
    except Exception as e:
        pass


def run_removebg_bythread(target, file_name, size, taskid):
    img_file_path = TEMP_FILE_PATH + file_name
    img_file = open(img_file_path, 'rb')

    api_key = get_api_key(target, taskid)

    response = requests.post(
        target.api_url,
        files={'image_file': img_file},
        data={'size': size},
        headers={'X-Api-Key': api_key})

    new_img_name = file_name + "_no_bg.png"

    if response.status_code == requests.codes.ok:
        new_img_path = TEMP_FILE_PATH + new_img_name
        with open(new_img_path, 'wb') as removed_bg_file:
            removed_bg_file.write(response.content)
            target.task_ids[taskid] = new_img_name
    elif response.status_code == requests.codes.payment:
        target.invalid_keys.append(api_key)
        target.task_ids[taskid] = 'error'
        print('api_key 失效了')
    else:
        target.task_ids[taskid] = 'error'
        print('其他异常')

    img_file.close()
    # time.sleep(5)
    print(threading.current_thread().name, new_img_name)


def get_api_key(target, taskid):
    keys = list(set(target.api_key).difference(set(target.invalid_keys)))
    if len(keys) > 0:
        return keys[0]
    else:
        target.task_ids[taskid] = 'error'
        print('没有可以使用的key了')
