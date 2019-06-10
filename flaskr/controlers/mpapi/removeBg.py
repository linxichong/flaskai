from enum import Enum
import json
import requests
from flaskr.base import CoreMixin
from removebg import RemoveBg
from ..mpapi import TEMP_FILE_PATH
import threading
import time


class RemoveBackgroud(CoreMixin):
    def __init__(self, core):
        super().__init__(core)
        self.api_key = self.core.config.get('REMOVEBG_API_KEY')
        self.api_url = self.core.config.get('REMOVEBG_API_URL')
        self.task_ids = {}

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
        try:
            img_name = self.task_ids.pop(taskid)
        except Exception as e:
            pass
        return img_name


def run_removebg_bythread(target, file_name, size, taskid):
    img_file_path = TEMP_FILE_PATH + file_name
    img_file = open(img_file_path, 'rb')
    response = requests.post(
        target.api_url,
        files={'image_file': img_file},
        data={'size': size},
        headers={'X-Api-Key': target.api_key})

    new_img_path = file_name + "_no_bg.png"

    if response.status_code == requests.codes.ok:
        with open(TEMP_FILE_PATH + new_img_path, 'wb') as removed_bg_file:
            removed_bg_file.write(response.content)
            target.task_ids[taskid] = new_img_path
    else:
        raise Exception()
   
    img_file.close()
    # time.sleep(5)
    print(threading.current_thread().name, new_img_path)
