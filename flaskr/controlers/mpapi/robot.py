from enum import Enum
import json
import requests
from flaskr.base import CoreMixin
from revChatGPT.V2 import Chatbot

class ChatRobot(CoreMixin):
    def __init__(self, core):
        super().__init__(core)

    def get_reply(self, input_text):
        raise NotImplementedError


# class TulingRobot(ChatRobot):
#     def __init__(self, core):
#         super().__init__(core)

#     def get_reply(self, input_text):
#         api_url = self.core.config.get('TULING_API_URL')
#         api_key = self.core.config.get('TULING_API_KEY')

#         param = {
#             "reqType": 0,
#             "perception": {
#                 "inputText": {
#                     "text": input_text
#                 },
#             },
#             "userInfo": {
#                 "apiKey": api_key,
#                 "userId": "demo"
#             }
#         }
#         req = json.dumps(param).encode('utf8')
#         resp = requests.post(api_url, data=req, headers={
#             'content-type': 'application/json'})
#         result = resp.json()
#         intent_code = result['intent']['code']
#         error_codes = [5000, 6000, 4000, 4001, 4002, 4003, 4005, 4007,
#                        4100, 4200, 4300, 4400, 4500, 4600, 4602, 7002, 8008, 0]
#         if not intent_code in error_codes:
#             text = ''
#             for res in result['results']:
#                 if res['resultType'] == 'text':
#                     text += res['values']['text']
#                 elif res['resultType'] == 'url':
#                     text += res['values']['url']
#                 text += '\n'
#             text = text.rstrip('\n')
#         else:
#             print('错误。错误代码：' + str(intent_code))
#         return text
    
class ChatGPTRobot(ChatRobot):
    def __init__(self, core):
        super().__init__(core)
        
        mail = self.core.config.get('CHAT_GPT_EMAIL')
        password = self.core.config.get('CHAT_GPT_PASSWORD')
        
        self.bot = Chatbot(email=mail, password=password)

    def get_reply(self, input_text):
        res = []
        for line in self.bot.ask(input_text):
            res.append(line["choices"][0]["text"].replace("<|im_end|>", ""), end="")

        return "\r\n".split(res)
