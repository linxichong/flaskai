
from urllib.parse import quote, urlparse, urlsplit

import requests
from pyquery import PyQuery as pq

from flaskr.base import CoreMixin

from multiprocessing.pool import Pool
from flaskr.common.utils import get_spider_db

from .base import BaseSpider
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import tesserocr
from PIL import Image

class SeleniumSpider(BaseSpider):
    def __init__(self, core):
        super().__init__(core)

    def find_jd_list(self, *args):
        keyword = args[0]
        url = 'https://search.jd.com/Search?keyword=%s' % quote(keyword)

        results = []

        try:
            brower = webdriver.Chrome()
            wait = WebDriverWait(brower, 10)
            brower.get(url)

            btn_prev = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.pn-prev')))
            btn_next = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.pn-next')))
            btn_next.send_keys(Keys.LEFT)

        except Exception as e:
            raise e

        return results
    
    def check_code(self, img_url):
        img = Image.open(img_url)
        threshold = 80
        img = img.convert('L')
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        img = img.point(table, '1')
        img.show()
        result = tesserocr.image_to_text(img)
        print(result)
