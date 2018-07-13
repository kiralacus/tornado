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
            username = self.get_current_user()['username']
            # username = '18351922521'
            sql = 'update ih_user_profile set up_avatar=%(up_avatar)s where up_name=%(username)s'
            self.db.execute(sql, up_avatar=imageName, username=username)
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
        username = self.get_current_user()['username']
        try:
            sql = 'select up_avatar from ih_user_profile where up_name=%(username)s'
            up_avatar = self.db.get(sql, username=username)
            avatar_url = up_avatar['up_avatar']
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='头像查询出错'))
        else:
            # 如果用户没有上传头像默认头像
            if not avatar_url:
                avatar_url = constants.DEFAULT_IMG

            url = constants.PRE_URL + avatar_url
            self.write(dict(errcode=RET.OK, errmsg='成功'))


    def post(self):
        pass




