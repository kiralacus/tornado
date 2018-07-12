# coding:utf-8

from utils.session import Session

import functools

from utils.response_code import RET


def require_login(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user:
            return self.write(dict(errcode=RET.SESSIONERR, errmsg='用户未登录'))
        else:
            return func(self, *args, **kwargs)
    return wrapper














