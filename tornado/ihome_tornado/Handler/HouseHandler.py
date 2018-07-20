#coding: utf-8

from Handler.BaseHandler import BaseHandler

from utils.response_code import RET

from utils.commons import require_login, require_auth

import config

import logging

import json

from utils.aliyun_storage import storage

import constants

import datetime


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


class NewHouseHandler(BaseHandler):
    '''房屋信息处理'''
    @require_login
    def post(self):
        '''
        :param {
            'title': --hi_title
            'price': --hi_price
            'area_id': --hi_area_id
            'address': --hi_address
            'room_count': --hi_room_count
            'acreage': --hi_acreage
            'unit': --hi_house_unit
            'capacity': --hi_capacity
            'beds':  --hi_beds
            'deposit': --hi_deposit
            'min_days': --hi_min_days
            'max_days': --hi_max_days
            'facility': --ih_house_facility
                            hf_house_id
                            hf_facility_id
            facility 是列表形式
        }
        :return:
        '''
        hi_user_id = self.get_current_user()['userId']
        hi_title = self.json_dict['title']
        hi_price = self.json_dict['price']
        hi_area_id = self.json_dict['area_id']
        hi_address = self.json_dict['address']
        hi_room_count = self.json_dict['room_count']
        hi_acreage = self.json_dict['acreage']
        hi_house_unit = self.json_dict['unit']
        hi_capacity = self.json_dict['capacity']
        hi_beds = self.json_dict['beds']
        hi_deposit = self.json_dict['deposit']
        hi_min_days = self.json_dict['min_days']
        hi_max_days = self.json_dict['max_days']
        hf_facility_id = self.json_dict['facility']

        # 存储入ih_house_info

        if not all((hi_user_id, hi_title, hi_price, hi_area_id, hi_address, hi_room_count, hi_acreage, hi_house_unit, hi_capacity, hi_beds, hi_deposit, hi_max_days, hi_min_days, hf_facility_id)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg='参数缺省'))

        try:
            hi_price = int(hi_price)
            hi_deposit = int(hi_deposit)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.PARAMERR, errmsg='参数错误'))

        try:
            # 房屋信息写入
            sql = 'insert into ih_house_info(hi_user_id, hi_title, hi_price, hi_area_id, hi_address, ' \
                  'hi_room_count, hi_acreage, hi_house_unit, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days) ' \
                  'values(%(hi_user_id)s, %(hi_title)s, %(hi_price)s, %(hi_area_id)s, %(hi_address)s, %(hi_room_count)s, ' \
                  '%(hi_acreage)s, %(hi_house_unit)s, %(hi_capacity)s, %(hi_beds)s, %(hi_deposit)s, %(hi_min_days)s, %(hi_max_days)s)'
            ret = self.db.execute(sql, hi_user_id=hi_user_id, hi_title=hi_title, hi_price=hi_price, hi_area_id=hi_area_id, hi_address=hi_address,
                            hi_room_count=hi_room_count, hi_acreage=hi_acreage, hi_house_unit=hi_house_unit, hi_capacity=hi_capacity, hi_beds=hi_beds,
                            hi_deposit=hi_deposit, hi_min_days=hi_min_days, hi_max_days=hi_max_days)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库写入错误'))
        else:
            # 设备信息写入
            try:
                sql = 'insert into ih_house_facility(hf_house_id, hf_facility_id) values'
                for each in hf_facility_id:
                    af = '(%s,%s),'%(ret, each)
                    sql += af
                sql = sql.rstrip(',')
                self.db.execute(sql)
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.DBERR, errmsg='数据库写入错误'))
            else:
                self.write(dict(errcode=RET.OK, errmsg='成功' , data=dict(houseID=ret)))


class HouseImageHandler(BaseHandler):
    '''处理上传照片'''
    @require_login
    def post(self):
        '''
        :param 传入参数： 文件数据流写入 house-image
         url传入          house-id

        :return:
        '''
        hi_house_image = self.request.files['house_image'][0]['body']
        # 使用ajax设置url后面带参数出错
        # 這裏採用<input type='hidden'>中的value
        hi_house_id = self.get_argument('houseid')
        # hi_house_id = self.json_dict['houseID']

        try:
            imageName = storage(hi_house_image)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.THIRDERR, errmsg='阿里云上传头像出错'))
        # 图片的完整url
        url = constants.PRE_URL + imageName
        try:
            sql = 'update ih_house_info set hi_index_image_url=%(url)s where hi_house_id=%(hi_house_id)s'
            self.db.execute(sql, url=imageName, hi_house_id=hi_house_id)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库出错'))
        else:
            self.write(dict(errcode=RET.OK, errmsg='成功', data=dict(url=url)))


class MyHouseHandler(BaseHandler):
    '''单个房主的房屋管理'''
    @require_login
    @require_auth
    def get(self):
        '''
        :param
        从ih_house_info中获取
        hi_house_id
        hi_title
        hi_area_id + hi_address
        hi_price
        hi_ctime
        :return:
        '''
        user_id = self.get_current_user()['userId']
        try:
            sql = 'select ai_name, hi_house_id, hi_title, hi_price, hi_address, hi_ctime, hi_index_image_url from ih_house_info left join ih_area_info ' \
                  'on ih_area_info.ai_area_id = ih_house_info.hi_area_id where hi_user_id=%(user_id)s'
            myhouseinfo = self.db.query(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
        else:
            # 获取hi_area_id对应信息
            houseList = []
            for each in myhouseinfo:
                myhouse = {}
                myhouse['area_name'] = each['ai_name'] + ' ' + each['hi_address']
                myhouse['house_id'] = each['hi_house_id']
                myhouse['title'] = each['hi_title']
                myhouse['price'] = each['hi_price']
                myhouse['ctime'] = str(each['hi_ctime'])
                if not each['hi_index_image_url']:
                    each['hi_index_image_url'] = constants.DEFAULT_HOUSE_IMG
                myhouse['imageUrl'] = constants.PRE_URL + each['hi_index_image_url']

                houseList.append(myhouse)

            self.write(dict(errcode=RET.OK, errmsg='成功', data=houseList))


class HouseDetailHandler(BaseHandler):
    '''处理详细房屋信息'''
    def get(self):
        '''
        :param -> house_id
               <- hi_acreage
                  hi_unit
                  hi_room_count
                  hi_capacity
                  hi_beds
                  hi_deposit
                  hi_min_days
                  hi_max_days
                  通过house_id在ih_house_facility中检索
        :return:
        '''
        house_id = self.get_argument()
        try:
            sql = 'select hi_acreage, hi_unit, hi_room_count, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days ' \
                  'from ih_house_info where house_id=%(house_id)s'
            houseDetail = self.db.get(sql, house_id=house_id)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
        else:
            try:
                sql = 'select hf_facility_id from ih_house_facility where hf_house_id=%(house_id)s'
                facility = self.db.query(sql, house_id)
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
            else:
                house_detail = {}
                house_detail['acreage'] = houseDetail['hi_acreage']
                house_detail['unit'] = houseDetail['hi_unit']
                house_detail['room_count'] = houseDetail['hi_room_count']
                house_detail['capacity'] = houseDetail['hi_capacity']
                house_detail['beds'] = houseDetail['hi_beds']
                house_detail['deposit'] = houseDetail['hi_deposit']
                house_detail['min_days'] = houseDetail['hi_min_days']
                house_detail['max_days'] = houseDetail['hi_max_days']
                house_detail['facility'] = []
                for each in facility:
                    house_detail['facility'].append(each['hf_facility_id'])
                self.write(dict(errcode=RET.OK, errmsg='ok', data=house_detail))



