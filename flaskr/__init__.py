import hashlib
import os

from flask import Flask, request, g, flash, render_template, current_app
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.utils import check_signature
from cachelib import SimpleCache
# from werkzeug.contrib.cache import SimpleCache
from instance.config import Config

cache = SimpleCache()
# wechat = WechatServer()
# access_token = wechat.access_token

def create_app(test_config=None):
    ''' instance_relative_config=True是用来告诉应用程序，
    配置文件是与实例文件夹（instance folder）相关联的。
    这个实例文件夹位于flaskr包的外部，
    并且它可以保存不应该提交到版本控制的本地数据，比如配置密钥和数据库文件。'''
    app = Flask(__name__, instance_relative_config=True)
    # # 设置一些应用程序会用到的默认配置
    # app.config.from_object('instance.config.Config')

    if test_config is None:
        app.config.from_object('instance.config.%s' %
                               app.config['ENV'].capitalize())
    else:
        app.config.from_mapping(test_config)
       
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cache.add('config', app.config, timeout=0)

    from . import wxmp
    app.register_blueprint(wxmp.bp)

    from . import spider
    app.register_blueprint(spider.bp)
    
    @app.route('/')
    def hello():
        text = 'Hello World!'
        return render_template('index.html',  name=text)

    return app
