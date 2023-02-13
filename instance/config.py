class Config:
    # 公众号开发信息
    # 开发者ID
    APP_ID= 'wx696092d42610689f'
    # 开发者密码
    APP_SECRET= 'd0d06e64962ad240b3267045337c4f7e'

    # 服务器配置
    # 令牌
    TOKEN = 'wl26JzbKfggZZbMH4MKJjji7rIMIgrvN'

    # 腾讯AI 人脸识别
    FACE_APP_ID = '2116712604'
    FACE_APP_KEY = 'hlYUQ4dNltZLZ9Q0'
    FACE_API_URL = 'https://api.ai.qq.com/fcgi-bin/face/face_detectface'
    # 图灵机器人
    TULING_API_URL = 'http://openapi.tuling123.com/openapi/api/v2'
    TULING_API_KEY = 'c9dd7250422742bc8f0405b12c655b6c'
    # 消除照片背景
    REMOVEBG_API_URL = 'https://api.remove.bg/v1.0/removebg'
    REMOVEBG_API_KEY = ['VM86pZ5o5ZMAqeLkgzujaLuv', 'yA3GCc4qTtZtoZkQZW5nRmmZ']
    
    CHAT_GPT_EMAIL = "gogailinxichong@gmail.com"
    CHAT_GPT_PASSWORD = "wk830725"


class Development(Config):
    SECRET_KEY = 'dev'

class Production(Config):
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

