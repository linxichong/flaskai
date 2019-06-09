from .storage import PickleStorage
from .token import TokenClass
from .face import FaceRecognition
from .robot import TulingRobot
from ..spiderapi.spider import BookSpider

class WechatServer:
    def __init__(self, config=None, atStorage=None):
        self.config = config
        self.atStorage = atStorage or PickleStorage()
        self.token = TokenClass(self)
        self.face = FaceRecognition(self)
        self.robot = TulingRobot(self)
        self.book_spider = BookSpider(self)
    
    def access_token(self, fn):
        return self.token.access_token(fn)
    
    def update_config(self, config=None, atStorage=None):
        self.config = config or self.config
        self.atStorage = atStorage or self.atStorage