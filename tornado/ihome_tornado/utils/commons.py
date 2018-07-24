# coding:utf-8

from utils.session import Session

import functools

from utils.response_code import RET

import logging


def require_login(func):
    '''
        1. 用户登录时执行装饰器下的函数
        2. 未登录时返回4101
    '''
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            return self.write(dict(errcode=RET.SESSIONERR, errmsg='用户未登录'))
        else:
            return func(self, *args, **kwargs)
    return wrapper


def require_auth(func):
    '''
        验证用户身份信息是否通过审核
    '''
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        user_id = self.get_current_user()['userId']
        try:
            sql = 'select up_auth from ih_user_profile where up_user_id=%(user_id)s'
            ret = self.db.get(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
        else:
            if ret['up_auth']:
                return func(self, *args, **kwargs)
            else:
                return self.write(dict(errcode=RET.USERERR, errmsg='用户尚未通过审核'))
    return wrapper










