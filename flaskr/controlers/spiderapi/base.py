
from .utils import get_user_agent
from flaskr.base import CoreMixin

class BaseSpider(CoreMixin):
    def __init__(self, core):
        super().__init__(core)
        self.headers = {'User-Agent': get_user_agent()}