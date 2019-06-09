from flask import Blueprint, request, current_app, make_response, redirect, url_for, g
import requests
import re

from flaskr import cache
from pyquery import PyQuery as pq

from flaskr.controlers.spiderapi.bookspider import BookSpider
from .common.utils import get_spider_db
import time

bp = Blueprint('spider', __name__)


@bp.route('/book', methods=['GET', 'POST'])
def book():
    try:
        spider = BookSpider(None)
        spider.find_all()
    except Exception as e:
        print(e)
        return 'fail'

    return 'success'


@bp.route('/other', methods=['GET', 'POST'])
def rar():
    try:
        spider = BookSpider(None)

        db = get_spider_db()
        colection = db.books
        r = colection.find()
        try:
            for rec in r:
                time.sleep(5)
                spider.find_other_info(rec['bookname'])
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        return 'fail'

    return 'success'
