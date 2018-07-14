# coding: utf-8

from Handler.BaseHandler import BaseHandler

import logging

from utils.response_code import RET

from hashlib import sha256

from utils.session import Session

from utils.commons import require_login

import config


class RegisterHandler(BaseHandler):
    '''存储用户信息'''
    def post(self):
        # 接受用户信息
        up_mobile = self.json_dict['mobile']
        phonecode = self.json_dict['phonecode']
        up_password = self.json_dict['password']
        # 判断数据是否完整
        if not all((up_mobile, phonecode, up_password)):
            self.write(dict(errcode=RET.DATAERR, errmsg='参数缺少'))
        else:
            # 判断手机号是否存在
            sql = "select up_mobile from ih_user_profile where up_mobile=%s"
            try:
                result = self.db.get(sql, up_mobile)
            except Exception as e:
                logging.error(e)
                self.write(errcode=RET.DBERR, errmsg='sql查询数据出错')
            else:
                if result:
                    self.write(dict(errcode=RET.DATAEXIST, errmsg='该手机号已存在'))
                else:
                    try:
                        phonecode_redis = self.redis.get('sms_code_%s'%up_mobile)
                    except Exception as e:
                        logging.error(e)
                        self.write(dict(errcode=RET.DBERR, errmsg='数据库查询出错'))
                    else:
                        # 该手机验证码不存在
                        if not phonecode_redis:
                            self.write(dict(errcode=RET.NODATA, errmsg='验证码不存在'))
                        # 验证手机验证码是否正确
                        elif phonecode != phonecode_redis:
                            self.write(dict(errcode=RET.DATAERR, errmsg='验证码输入错误'))
                        # 存储用户信息
                        else:
                            up_password = sha256(up_password).hexdigest()
                            sql = 'insert into ih_user_profile(up_name, up_mobile, up_passwd) ' \
                                  'values(%(up_name)s, %(up_mobile)s, %(up_password)s)'
                            try:
                                self.db.execute(sql, up_name = up_mobile, up_mobile=up_mobile, up_password=up_password)
                            except Exception as e:
                                logging.error(e)
                                self.write(dict(errcode=RET.DBERR, errmsg='sql数据库插入错误'))
                            else:
                                self.write(dict(errcode=RET.OK, errmsg='成功'))


class LoginHandler(BaseHandler):
    '''用户登录'''
    def post(self):
        mobile = self.json_dict.get('mobile')
        password = self.json_dict.get('password')
        print password
        if not all((mobile, password)):
            self.write(dict(errcode=RET.DATAERR, errmsg='参数缺少'))
        else:
            # 判断数据库中是否存在该数据
            try:
                # 判断用户名是否存在
                sql = 'select up_user_id from ih_user_profile where up_mobile=%(mobile)s'
                sql_id = self.db.get(sql, mobile=mobile)
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
            else:
                # 用户不存在
                if not sql_id:
                    self.write(dict(errcode=RET.USERERR, errmsg='用户不存在'))
                # 用户存在
                else:
                    try:
                        passwd_sql = 'select up_passwd from ih_user_profile where up_mobile=%(mobile)s'
                        sql_password = self.db.get(passwd_sql, mobile=mobile)
                    except Exception as e:
                        logging.error(e)
                        self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))

                    else:
                        # 密码错误
                        if sql_password['up_passwd'] != sha256(config.passwd_salt+password).hexdigest():
                            print sha256(password).hexdigest()
                            self.write(dict(errcode=RET.PWDERR, errmsg='密码错误'))

                        else:
                            self.write(dict(errcode=RET.OK, errmsg='登陆成功'))
                            session = Session(self)
                            session.data['mobile'] = mobile
                            session.save()


class CheckLoginHandler(BaseHandler):
    '''检查是否登录'''
    def get(self):
        if self.get_current_user():
            return self.write(dict(errcode=RET.OK, errmsg='用户已登录', data=self.get_current_user()['username']))
        else:
            return self.write(dict(errcode=RET.SESSIONERR, errmsg='用户未登录'))


class LogoutHandler(BaseHandler):
    '''登出操作'''
    @require_login
    def get(self):
        session = Session(self)
        sess_id = session.session_id
        session.clear()
        # 判断是否删除session数据
        user = self.redis.get('sess_id_%s'%sess_id)
        print user
        if not user:
            print 'logout'
            self.write(dict(errcode=RET.OK, errmsg='登出成功'))
        else:
            self.write(dict(errcode=RET.DBERR, errmsg='登出失败'))

