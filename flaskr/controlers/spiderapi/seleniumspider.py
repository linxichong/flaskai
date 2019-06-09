
from urllib.parse import quote, urlparse, urlsplit

import requests
from pyquery import PyQuery as pq

from flaskr.base import CoreMixin

from multiprocessing.pool import Pool
from flaskr.common.utils import get_spider_db

from .base import BaseSpider
from selenium import webdriver

class SeleniumSpider(BaseSpider):
    def __init__(self, core):
        super().__init__(core)

    def find(self, *args):
        keyword = args[0]
        url = 'https://search.jd.com/Search?keyword=%s' % quote(keyword)

        results = []
        
        brower = webdriver.Chrome()
        brower.get(url)
        try:
            pass
        except Exception as e:
            raise e

        return results