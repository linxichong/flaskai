    
import pickle, logging, sys
from ..mpapi import INSTANCE_PATH


class AccessTokenStorage:
    def get_access_token(self):
        raise NotImplementedError()
    def store_access_token(self, accessToken, expireTime):
        raise NotImplementedError()

class PickleStorage(AccessTokenStorage):
    ''' storage for test use
        {
            'accessToken': ('', 0),
            'serverList': ([], 0),
        }
    '''
    def __init__(self):
        try:
            with open(INSTANCE_PATH + 'storage.pkl', 'rb') as f:
                self.__storageDict = pickle.load(f)
        except:
            print('storage not found')
            self.__storageDict = {}
    def __store_locally(self):
        try:
            with open(INSTANCE_PATH + 'storage.pkl', 'wb') as f:
                pickle.dump(self.__storageDict, f)
        except:
            pass
    def get_access_token(self):
        return self.__storageDict.get('accessToken', ('', 0))
    def store_access_token(self, accessToken, expireTime):
        self.__storageDict['accessToken'] = (accessToken, expireTime)
        self.__store_locally()
        print('Access token updated')