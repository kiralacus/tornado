#coding: utf-8
import random

from BaseHandler import BaseHandler

from utils.captcha.captcha import captcha

import constants

import logging

from lib.yuntongxun.SendTemplateSMS import CCP

from utils.response_code import RET


class PicCodeHandler(BaseHandler):
    '''图片验证码'''
    def get(self):
        '''获取验证码图片id'''
        pre_code_id = self.get_argument('precodeid')
        cur_code_id = self.get_argument('codeid')
        # 生成验证码图片
        name, text, pic = captcha.generate_captcha()
        try:
            if pre_code_id:
                self.redis.delete('pic_code_%s'%pre_code_id)

            self.redis.setex('pic_code_%s'%cur_code_id, constants.PIC_CODE_EXPIRE_SECONDS, text)
        except Exception as e:
            logging.error(e)
            self.write("")
        else:
            self.set_header('Content-Type', 'image/jpg')
            self.write(pic)


class SMSCodeHandler(BaseHandler):
    '''手机验证码'''
    def post(self):
        mobile = self.json_dict.get('mobile')
        piccode = self.json_dict.get('piccode')
        piccode_id = self.json_dict.get('piccode_id')
        # 判断数据是否存在
        if not all((mobile, piccode, piccode_id)):
            self.write(dict(errcode=RET.NODATA, errmsg='数据不完整'))
        else:
            # 判断数据库中该手机是否存在
            try:
                sql = "select up_mobile from ih_user_profile where up_mobile=%(mobile)s"
                sql_mobile = self.db.get(sql, **dict(mobile=mobile))
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.DBERR, errmsg='sql数据库查询错误'))
            else:
                if sql_mobile:
                    self.write(dict(errcode=RET.DATAEXIST, errmsg='该手机号已存在'))
                else:
                    # 判断图片验证码输入是否正确
                    try:
                        redis_piccode = self.redis.get('pic_code_%s'%piccode_id)
                    except Exception as e:
                        logging.error(e)
                        self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
                    else:
                        # 数据中不存在此数据或此数据失效
                        if not redis_piccode:
                            self.write(dict(errcode=RET.NODATA, errmsg='数据库中不存在此数据'))
                        else:
                            # 如果数据输入错误
                            if not piccode.lower() == redis_piccode.lower():
                                self.write(dict(errcode=RET.PARAMERR, errmsg='验证码输入错误'))
                            # 验证码正确输入
                            else:
                                # 生成手机验证码
                                code = '%04d'%random.randint(1, 10000)
                                try:
                                    # 存储手机验证码
                                    self.redis.setex("sms_code_%s"%mobile, constants.SMS_CODE_EXPIRE_SECONDS, code)
                                except Exception as e:
                                    self.write(dict(errcode=RET.DBERR, errmsg='验证码写入错误'))
                                # 手机验证码
                                ccp = CCP.instance()
                                try:
                                    result = ccp.sendTemplateSMS(mobile, [code, constants.SMS_CODE_EXPIRE_SECONDS/60], 1)
                                except Exception as e:
                                    logging.error(e)
                                    self.write(dict(errcode=RET.THIRDERR, errmsg='发送短信失败'))
                                else:
                                    if result:
                                        self.write(dict(errcode=RET.OK, errmsg='短信发送成功'))
                                    else:
                                        self.write(dict(errcode=RET.THIRDERR, errmsg='短信发送失败'))








