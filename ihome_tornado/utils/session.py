# coding:utf-8

import uuid

import config

import logging

import json


class Session(object):
    def __init__(self, request_Handler_obj):
        self.requestHandler = request_Handler_obj
        self.data = {}
        self.session_id = self.requestHandler.get_secure_cookie('sess_id')
        # 如果cookie中不含有session_id
        if not self.session_id:
            session_id = uuid.uuid4().get_hex()
            self.requestHandler.set_secure_cookie('sess_id', session_id)
            self.data = {}

        else:
            try:
                json_data = self.requestHandler.redis.get('sess_id_%s'%self.session_id)
            except Exception as e:
                logging.error(e)
                raise e
            else:
            # 如果json_data 失效
                if not json_data:
                    self.data = {}
                else:
                    json_data = json.loads(json_data)

    def save(self):
        json_data = json.dumps(self.data)
        try:
            self.requestHandler.redis.setex('sess_id_%s'%self.session_id, config.session_expire_seconds, json_data)
        except Exception as e:
            logging.error(e)
            raise(e)

    def clear(self):
        self.requestHandler.clear_cookie('sess_id')
        try:
            self.requestHandler.delete("sess_id_%s"%self.session_id)
        except Exception as e:
            logging.error(e)
            pass







