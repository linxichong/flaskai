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
# 初始化微信服务实例
wechat = WechatServer(cache.get('config'))
# 菜单命令
commands = {
    # 'm1': '开启聊天机器人',
    'm2': '小说下载',
    'm3': '消除照片背景',
    'm4': '美照评分',
    'b': '返回主菜单'}
# 缓存的命令菜单
command_domain = {}
# 缓存的消息ID序列
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
        # 转换消息对象
        xml = request.stream.read()
        msg = parse_message(xml)
        # 返回结果
        response = None
        # 处理超时
        response = handle_time_out(msg)
        if response:
            return response, 200
        # 处理菜单功能上下文环境
        response = handle_func_context(msg)
        if response:
            return response, 200

        # 获取功能菜单
        funcId = command_domain.get(msg.source)
        # 调用图灵聊天机器人（需要认证暂时关闭）
        if funcId == 'm1':
            resp_xml = call_tuling_robot(msg)
        # 小说查询
        elif funcId == 'm2':
            resp_xml = call_find_novel(msg)
        # 消除照片背景
        elif funcId == 'm3':
            resp_xml = remove_img_bg(msg)
        # 美照评分
        elif funcId == 'm4':
            resp_xml = photo_score(msg)
        else:
            pass

        # if msg.type in 'text':
        #     resp_xml = handle_text_voice_msg(msg)
        # elif msg.type == 'image':
        #     resp_xml = handle_image_msg(msg)
        #     delete_temp_file()
        # else:
        #     print(msg.type)

        response = make_response(resp_xml)
        return response, 200


'''
微信服务器5秒内收不到回应，会重发3次,通过message_id排重，
解决后台任务时间过长公众号服务故障
'''


def handle_time_out(msg):
    if msg.id in message_ids:
        resp_xml = create_reply(
            '客官的要求有点复杂，店小二正在处理，请稍后再试！', message=msg, render=True)
        return make_response(resp_xml)

    message_ids.append(msg.id)


'''
根据菜单命令处理功能开启/关闭
'''


def handle_func_context(msg):
    resp_xml = None
    cmd = command_domain.get(msg.source)
    is_back = False

    if cmd == None:
        if msg.type != 'text':
            is_back = True
        elif commands.get(msg.content):
            resp_xml = create_reply('%s[功能开启]' %
                                    commands.get(msg.content), message=msg, render=True)
            command_domain[msg.source] = msg.content
            return make_response(resp_xml)
        else:
            is_back = True
    elif msg.type == 'text':
        if msg.content == 'b':
            is_back = True
        elif msg.content == 't':
            wechat.rmBg.add_bgcolor('img-2019_08_3123_35_01.jpg_no_bg.png')

    if is_back:
        command_domain.clear()
        resp_xml = get_menu_reply(msg)
        return make_response(resp_xml)

    return None


'''
使用微信提供的语音解析功能获取转换结果
'''


def handle_voice_msg(msg):
    return msg.recognition


'''
调用图灵聊天机器人
'''


def call_tuling_robot(msg):
    resp_xml = None
    try:
        resp_xml, content = '', None
        if msg.type == 'voice':
            content = msg.recognition
        elif msg.type == 'text':
            content = msg.content

        text = wechat.robot.get_reply(msg.content)
        resp_xml = create_reply(text, message=msg, render=True)
    except Exception as e:
        resp_xml = get_error_reply(msg)

    return resp_xml

'''
调用小说查询
'''


def call_find_novel(msg):
    if msg.type != 'text':
        return get_error_reply(msg)
    resp_xml = None
    data = ''
    try:
        db = get_spider_db()
        colection = db.books

        results = colection.find({'full_text': re.compile(msg.content)})
        if results.count() == 0:
            data = '客官，您要的书没找到也，换换别的吧。'

        size = results.count() if isinstance(results, Cursor) else len(results)
        max_size = 10
        if size >= 1:
            text = ''
            index = 0
            for rec in results:
                if index >= max_size:
                    break
                index = index + 1
                text += '%s %s(%s)\n%s\n' % (rec.get('bookname'), rec.get(
                    'booktype', ''), rec.get('author'), rec.get('download_url'))
            if size > max_size:
                data += '满足条件的小说共%s本，现仅列出前10本，请重新输入查询条件精确查找：\n\n' % size
            data += text[:-1]
        # elif size == 1:
        #     data.append(get_article(results[0]))
        # else:
        #     data = '客官，您要的书没找到也，换换别的吧。'

        resp_xml = create_reply(data, message=msg, render=True)
    except Exception as e:
        resp_xml = get_error_reply(msg)

    return resp_xml


'''
消除照片背景
'''


@wechat.access_token
def remove_img_bg(msg, accessToken=None):
    resp_xml = None

    try:
        if msg.type == 'text':
            no_bg_img_path = wechat.rmBg.get_result_bytaskid(msg.content)
            if no_bg_img_path:
                media_id = upload(
                    'image', no_bg_img_path, accessToken)
                from wechatpy.messages import ImageMessage
                newMsg = ImageMessage(msg._data)
                reply = ImageReply(media_id=media_id, message=newMsg)
                return reply.render()
            else:
                return get_imgerr_reply(msg)

        # 通过公众号接收到的图片信息下载图片到本地
        path = download(msg.image, msg.source)
        # 调用ai去除背景接口，保存结果图片后，返回对应路径
        taskid = wechat.rmBg.do_remove(path)

        import threading
        print(threading.current_thread().name, taskid)

        text = '下载注意事项：请用[5a4490.../red]的格式发送消息，用于下载处理后图像文件。\n颜色默认为白色(white)，同时支持红色(red),蓝色(blue)。\n验证码：%s' % taskid
        resp_xml = create_reply(
            text, message=msg, render=True)

    except Exception as e:
        resp_xml = get_error_reply(msg)

    return resp_xml


'''
调用美图评分
'''


@wechat.access_token
def photo_score(msg, accessToken=None):
    if msg.type != 'image':
        return get_imgerr_reply(msg)

    resp_xml = None
    try:
        # 通过公众号接收到的图片信息下载图片到本地
        path = download(msg.image, msg.source)
        # 调用腾讯ai人脸识别接口接口
        r = wechat.face.access_api(path)
        if r == 'success':
            # 上传图片，得到 media_id
            media_id = upload(
                'image', path, accessToken)
            reply = ImageReply(media_id=media_id, message=msg)
        else:
            reply = TextReply(content='人脸检测失败，请上传1M以下人脸清晰的照片', message=msg)
        resp_xml = reply.render()
    except Exception as e:
        resp_xml = get_error_reply(msg)

    return resp_xml


# def get_article(data):
#     print(data)
#     return {
#         'title': data.get('bookname'),
#         'description': '%s %s' % (data.get('author'), data.get('booktype')),
#         'image': data.get('img_url'),
#         'url': data.get('download_url') + '?&from=singlemessage&isappinstalled=0'
#     }


'''
生成通用异常回复消息
'''


def get_error_reply(msg):
    return create_reply(
        '服务出现异常，请稍后再试。', message=msg, render=True)


'''
生成图片类通用异常回复消息
'''


def get_imgerr_reply(msg):
    return create_reply(
        '请上传需要处理的图片。', message=msg, render=True)


'''
生成菜单回复消息
'''


def get_menu_reply(msg):
    menu = '公众号开放功能菜单:\n'
    for key, val in commands.items():
        menu += '%s: %s \n' % (key, val)
    return create_reply(
        menu[:-1], message=msg, render=True)
