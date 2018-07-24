# coding: utf-8
import tornado

import json

from tornado import web

from utils.session import Session


class BaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        ''''''
        # 对传入的json进行预处理, 将其存储于self.json_dict中
        self.xsrf_token
        if self.request.headers.get('Content-Type','').startswith('application/json'):
            self.json_dict = json.loads(self.request.body)
        else:
            # self.json_dict = None
            self.json_dict = {} # 这样.get 就不会出错

    def write_error(self, *args, **kwargs):
        pass

    def set_default_header(self):
        pass

    def initialize(self):
        pass

    def on_finish(self):
        pass

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def get_current_user(self):
        '''
            self.session.data = {
                'mobile':
                'username':
            }
        '''
        self.session = Session(self)
        return self.session.data


class StaticFileHandler(tornado.web.StaticFileHandler):
    '''在网页中触发设置_xsrf'''
    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)
        self.xsrf_token

