#coding: utf-8
from Handler.BaseHandler import BaseHandler

from utils.response_code import RET

from utils.commons import require_login

import config

import logging

import json


class IndexHandler(BaseHandler):
    '''获取地域信息'''
    def get(self):
        '''
        先从redis中尝试获取地域信息
        从ih_area_info中读取ai_area_id, ai_name
        将这些数据存储于redis数据库中
        :return:{'errcode':, 'errmsg':, 'data':{'id':, 'name':}}
        '''
        # 尝试从redis中取数据
        try:
            areaList = self.redis.get('areaList')
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据查询错误'))
        else:
            if areaList:
                self.write('"errcode":"0", "errmsg":"成功", "data": %s'%areaList)
            else:
                # 从Mysql中获取ih_area_info
                try:
                    sql = 'select ai_area_id, ai_name from ih_area_info'
                    ih_area_info = self.db.query(sql)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误o'))
                else:
                    # ih_area_info是形如[{},{}], 中间是类字典, 需将其中数据拿出来重组
                    areaInfo = {}
                    areaList = []
                    for each in ih_area_info:
                        areaInfo['id']  = each['ai_area_id']
                        areaInfo['name'] = each['ai_name']
                        areaList.append(areaInfo)
                    # 将areaList字符串之后以hash形式存储在redis之中
                    areaList_json = json.dumps(areaList)
                    try:
                        self.redis.setex('areaList', config.areainfo_expire_seconds, areaList_json)
                    except Exception as e:
                        logging.error(e)
                        self.write(dict(errcode=RET.DBERR, errmsg='redis数据存储出错'))
                    else:
                        self.write(dict(errcode=RET.OK, errmsg='成功', data=areaList))


