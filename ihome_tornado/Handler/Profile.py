#coding:utf-8

from Handler.BaseHandler import BaseHandler

from utils.session import Session

from utils.aliyun_storage import storage

from utils.response_code import RET

from utils.commons import require_login

import logging

import constants


class AvatarHandler(BaseHandler):
    '''头像上传'''
    @require_login
    def post(self):
        imageData = self.request.files['avatar'][0]['body']
        # print imageData
        imageName = storage(imageData)
        print imageName
        # 图片的完整url
        url = constants.PRE_URL + imageName

        try:
            # 修改当前用户的头像
            up_mobile = self.get_current_user()['mobile']
            # username = '18351922521'
            sql = 'update ih_user_profile set up_avatar=%(up_avatar)s where up_mobile=%(up_mobile)s'
            self.db.execute(sql, up_avatar=imageName, up_mobile=up_mobile)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='图片存储失败'))
        else:
            self.write(dict(errcode=RET.OK, errmsg='成功', data=url))


class ProfileHandler(BaseHandler):
    '''获取ih_user_profile中数据'''
    @require_login
    def get(self):
        '''获取头像url'''
        mobile = self.get_current_user()['mobile']
        # username = '18351922521'
        try:
            sql = 'select up_avatar, up_name, up_mobile from ih_user_profile where up_mobile=%(up_mobile)s'
            info = self.db.get(sql, up_mobile=mobile)
            avatar_url = info['up_avatar']
            up_name = info['up_name']
            up_mobile = info['up_mobile']
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='头像查询出错'))
        else:
            # 如果用户没有上传头像默认头像
            if not avatar_url:
                avatar_url = constants.DEFAULT_IMG
                # 将其存储于数据库中
                try:
                    sql = 'update ih_user_profile set up_avatar=%(up_avatar)s where up_mobile=%(mobile)s'
                    self.db.execute(sql, up_avatar=avatar_url, mobile=mobile)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='头像数据写入出错'))

            url = constants.PRE_URL + avatar_url
            self.write(dict(errcode=RET.OK, errmsg='成功', data=dict(avatar=url, up_name=up_name, up_mobile=up_mobile)))


class NameHandler(BaseHandler):
    '''修改up_name'''
    # @require_login
    def post(self):
        print 'i am in NameHandler'
        up_name = self.json_dict['name']
        up_mobile = self.get_current_user()['mobile']
        # up_mobile = '18351922521'
        # 判断数据库中是否已存在该数据
        try:
            sql = 'select up_name from ih_user_profile where up_name=%(up_name)s'
            result = self.db.get(sql, up_name=up_name)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='用户姓名查询出错'))
        else:
            if result:
                print 1
                self.write(dict(errcode=RET.DATAEXIST, errmsg='用户姓名已存在'))
            else:
                try:
                    sql = 'update ih_user_profile set up_name=%(up_name)s where up_mobile=%(up_mobile)s'
                    self.db.execute(sql, up_name=up_name, up_mobile=up_mobile)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='用户姓名写入出错'))
                else:
                    self.write(dict(errcode=RET.OK, errmsg='成功'))


class AuthHandler(BaseHandler):
    '''实名认证处理'''
    @require_login
    def get(self):
        '''
            从数据库中获取
            up_real_name:
            up_id_card:
        '''
        mobile = self.get_current_user()['mobile']
        # mobile = '18351922521'
        try:
            sql = 'select up_real_name, up_id_card from ih_user_profile where up_mobile=%(up_mobile)s'
            authinfo = self.db.get(sql, up_mobile=mobile)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='身份认证数据查询出错'))
        else:
            up_real_name = authinfo['up_real_name']
            up_id_card = authinfo['up_id_card']
            if not all((up_real_name, up_id_card)):
                # 只要其中有一个空， 都传这个信息
                self.write(dict(errcode=RET.USERERR, errmsg='身份未认证'))
            else:
                self.write(dict(errcode=RET.OK, errmsg='成功', data=dict(up_real_name=up_real_name, up_id_card=up_id_card)))

    # @require_login
    def post(self):
        '''
            想数据库存储
            传入参数：
                real_name
                id_card
            存储参数
                up_real_name
                up_id_card
        '''
        # mobile = self.get_current_user()['mobile']
        mobile = '18351922521'
        up_real_name = self.json_dict['real_name']
        up_id_card = self.json_dict['id_card']
        try:
            sql = 'update ih_user_profile set up_real_name=%(up_real_name)s, up_id_card=%(up_id_card)s where up_mobile=%(up_mobile)s'
            self.db.execute(sql, up_real_name=up_real_name, up_id_card=up_id_card, up_mobile=mobile)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据更新出错'))
        else:
            self.write(dict(errcode=RET.OK, errmsg='成功'))
