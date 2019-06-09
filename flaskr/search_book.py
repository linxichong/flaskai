from flask import Blueprint, request, current_app, make_response, redirect, url_for, g
import requests
import re
from pymongo import MongoClient

from flaskr import cache
from pyquery import PyQuery as pq

bp = Blueprint('book', __name__)

@bp.route('/book', methods=['GET', 'POST'])
def spider():

    clinet = MongoClient('localhost', port=27017)
    db = clinet.test
    colection = db.movies
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
    }

    target_url = 'http://www.zxcs.me/index.php?keyword=%E6%B2%99%E6%BC%A0'

    try:
        resp = requests.get(target_url, headers=headers)
        doc = pq(resp.text)
        dd_list_tag = doc.find('dd')
        
        record = []
        
        for dd_tag in dd_list_tag.items():
            rank = dd_tag.find('i.board-index').text()
            name = dd_tag.find('a.image-link').attr('title')
            img_uri = dd_tag.find('img.board-img').attr('data-src')
            actor = dd_tag.find('p.star').text()
            time = dd_tag.find('p.releasetime').text()
            movie = {}
            movie['rank'] = rank
            movie['name'] = name
            movie['uri'] = img_uri
            movie['actor'] = actor
            movie['time'] = time
            record.append(movie)
            
            # record.append([rank, name, img_uri, actor, time])
        colection.insert_many(record)
        # with open('maoyan_movie.txt', 'w', encoding='utf-8') as f:
        #     for item in record:
        #         text = ','.join(item)
        #         f.write(text + '\n')
            
    except Exception as e:
        current_app.logger.info(e)
    
    return 'Hello Spider!'
    # patten = re.compile('', re.S)

@bp.route('/list', methods=['GET', 'POST'])
def list():

    clinet = MongoClient('localhost', port=27017)
    db = clinet.test
    colection = db.movies

    results = ''
    for item in colection.find():
        results += str(item) + '\n'
    
    return results
    # patten = re.compile('', re.S)
