import os
import re
import time

from flask import (Blueprint, current_app, g, make_response, redirect, request,
                   url_for)
from pymongo import MongoClient
from pymongo.cursor import Cursor
from wechatpy import parse_message, create_reply
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.replies import ImageReply, TextReply, ArticlesReply
from wechatpy.utils import check_signature
from .common.utils import get_spider_db

from flaskr import cache

from .controlers.mpapi.server import WechatServer
from .controlers.mpapi.utils import delete_temp_file, download, upload

bp = Blueprint('wxmp', __name__)

wechat = WechatServer(cache.get('config'))

commands = {'M1': '开启聊天机器人',
            'M2': '小说下载',
            # 'M3': '人脸识别'
            'M3': '返回主菜单'}

command_domain = {}

message_ids = []


@bp.route('/weixin', methods=['GET', 'POST'])
def wxmp():
    if request.method == "GET":
        # 微信加密签名
        signature = request.args.get('signature')
        # 时间戳
        timestamp = request.args.get('timestamp')
        # 随机数
        nonce = request.args.get('nonce')
        # 随机字符串
        echostr = request.args.get('echostr')
        # 令牌(Token)
        token = current_app.config['TOKEN']

        try:
            check_signature(token, signature, timestamp, nonce)
            return echostr
        except InvalidSignatureException as e:
            current_app.logger.info(e)
    elif request.method == 'POST':
        xml = request.stream.read()
        msg = parse_message(xml)
        resp_xml = ''
        if msg.id in message_ids:
            resp_xml = create_reply(
                '客官的要求有点复杂，店小二正在处理，请稍后再试！', message=msg, render=True)
            response = make_response(resp_xml)
            return response, 200
        message_ids.append(msg.id)
        if msg.type in ['voice', 'text']:
            resp_xml = handle_text_voice_msg(msg)
        elif msg.type == 'image':
            resp_xml = handle_image_msg(msg)
            delete_temp_file()
        else:
            print(msg.type)

        response = make_response(resp_xml)
        return response, 200


def handle_text_voice_msg(msg):
    resp_xml, content = '', None
    if msg.type == 'voice':
        content = msg.recognition
    elif msg.type == 'text':
        content = msg.content

    if content == 'M3':
        if msg.source in command_domain:
            command_domain.pop(msg.source)
        resp_xml = create_reply(get_menu(commands), message=msg, render=True)
    elif command_domain.get(msg.source) == None:
        value = commands.get(content)
        if content == 'M1':
            resp_xml = create_reply('%s[功能开启]' %
                                    value, message=msg, render=True)
            command_domain[msg.source] = content
        elif content == 'M2':
            resp_xml = create_reply('%s[功能开启]' %
                                    value, message=msg, render=True)
            command_domain[msg.source] = content
        else:
            if msg.source in command_domain:
                command_domain.pop(msg.source)
            resp_xml = create_reply(
                get_menu(commands), message=msg, render=True)
    else:
        if command_domain.get(msg.source) == 'M1':
            text = wechat.robot.get_reply(content)
            resp_xml = create_reply(text, message=msg, render=True)
        elif command_domain.get(msg.source) == 'M2':
            resp_xml = handle_find_book(content, msg)
    return resp_xml


def handle_find_book(keyword, msg):
    resp_xml = None
    try:
        db = get_spider_db()
        colection =  db.books

        results = colection.find({'full_text': re.compile(keyword)})
        if results.count() == 0:
            results = wechat.book_spider.find(keyword)
            if len(results) > 0:
                colection.insert_many(results)

        data = []
        size = results.count() if isinstance(results, Cursor) else len(results)
        if size > 1:
            text = ''
            for rec in results:
                text += '%s %s(%s)\n%s\n' % (rec.get('bookname'), rec.get(
                    'booktype', ''), rec.get('author'), rec.get('download_url'))
            data = text[:-1]
        elif size == 1:
            data.append(get_article(results[0]))
        else:
            data = '客官，您要的书没找到也，换换别的吧。'

        resp_xml = create_reply(data, message=msg, render=True)
    except Exception as e:
        print(e)

    return resp_xml


@wechat.access_token
def handle_image_msg(msg, accessToken=None):
    name = download(msg.image, msg.source)  # 下载图片
    r = wechat.face.access_api(name)
    if r == 'success':
        media_id = upload(
            'image', name, accessToken)  # 上传图片，得到 media_id
        reply = ImageReply(media_id=media_id, message=msg)
    else:
        reply = TextReply(content='人脸检测失败，请上传1M以下人脸清晰的照片', message=msg)
    resp_xml = reply.render()
    return resp_xml


def get_article(data):
    return {
        'title': data.get('bookname'),
        'description': '%s %s %s' % (data.get('author'), data.get('booktype'), data.get('score')),
        'image': data.get('img_url'),
        'url': data.get('download_url')
    }


def get_menu(cmds):
    menu = '公众号开放功能菜单:\n'
    for key, val in cmds.items():
        menu += '%s: %s \n' % (key, val)
    return menu[:-1]
