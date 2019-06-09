from pymongo import MongoClient
import os

def get_spider_db():
    db_url = os.environ.get('MONGODB_URI')
    # db_url = 'mongodb://heroku_qmxbd0rq:ef13vosvbgegmocr09svn98h5@ds263816.mlab.com:63816/heroku_qmxbd0rq'

    clinet = MongoClient(db_url)
    return clinet['heroku_qmxbd0rq']
