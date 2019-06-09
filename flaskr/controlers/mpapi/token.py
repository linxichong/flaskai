import functools
import logging
import time
import threading
import traceback
from datetime import datetime, timedelta

from requests import get
from requests.models import Response
from requests.sessions import session
from flaskr.base import CoreMixin
from ..mpapi import SERVER_URL, GET_TOKEN_URL

# logger = logging.getLogger('flaskai')


class BaseTokenClass(CoreMixin):
    def __init__(self, core, tokenUrl):
        super().__init__(core)
        self.tokenUrl = tokenUrl
        self._session = session()
        self._session.verify = False
        self._accessTokenFunction = self.access_token_producer()

    def update_access_token(self):
        url = self.tokenUrl % (self.core.config.get(
            'APP_ID'), self.core.config.get('APP_SECRET'))
        r = self._session.get(url).json()
        if 'access_token' in r:
            self.core.atStorage.store_access_token(
                r['access_token'], int(time.time()) + r['expires_in'])
        else:
            print('Failed to get token: %s' % r)
        return r

    def access_token_producer(self):
        def _access_token(fn):
            @functools.wraps(fn)
            def __access_token(*args, **kwargs):
                accessToken, expireTime = self.core.atStorage.get_access_token()
                if expireTime < time.time():
                    updateResult = self.update_access_token()
                    if not updateResult:
                        return updateResult
                    accessToken, expireTime = self.core.atStorage.get_access_token()
                kwargs['accessToken'] = accessToken
                r = fn(*args, **kwargs)
                try:
                    errcode = r.json().get('errcode')
                    isTokenTimeout = errcode == 40014
                except:
                    isTokenTimeout = False
                if isinstance(r, Response) and isTokenTimeout:
                    updateResult = self.update_access_token()
                    if not updateResult:
                        return updateResult
                    accessToken, expireTime = self.core.atStorage.get_access_token()
                    kwargs['accessToken'] = accessToken
                    r = fn(*args, **kwargs)
                return r
            return __access_token
        return _access_token

    def access_token(self, fn):
        return self._accessTokenFunction(fn)


class TokenClass(BaseTokenClass):
    def __init__(self, core):
        super().__init__(core, SERVER_URL + GET_TOKEN_URL)
