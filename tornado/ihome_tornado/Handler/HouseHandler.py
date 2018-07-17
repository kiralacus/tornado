#coding: utf-8

from Handler.BaseHandler import BaseHandler

from utils.response_code import RET

from utils.commons import require_login

import config

import logging

import json


class AreaHandler(BaseHandler):
    '''获取地域信息'''
    @require_login
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
                # 这里前端解析出现问题当write中为字符串时（确保json格式无误）,前端无法正常解析
                areaList = json.loads(areaList)
                self.write(dict(errcode=RET.OK, errmsg='成功', data=areaList))
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
                    # areaInfo = {}
                    areaList = []
                    for each in ih_area_info:
                        # 列表这个东西和有意思，如果在外边初始化他甚至可以修改列表前面的几项相同key值的value
                        areaInfo = {}
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


class MyHouseHandler(BaseHandler):
    '''房屋信息处理'''
    def post(self):
        '''
        :param {
            'titile': --hi_title
            'price': --hi_price
            'area_id': --hi_area_id
            'address': --hi_address
            'room_count': --hi_room_count
            'acreage': --hi_acreage
            'unit': --hi_house_unit
            'capacity': --hi_capacity
            'beds':  --hi_beds
            'deposity': --hi_deposity
            'min_days': --hi_min_days
            'max_days': --hi_max_days
            'facility': --ih_house_facility
                            hf_house_id
                            hf_facility_id
        }
        :return:
        '''
