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

import math

import datetime


class AreaHandler(BaseHandler):
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
        hi_title = self.json_dict.get('title')
        hi_price = self.json_dict.get('price')
        hi_area_id = self.json_dict.get('area_id')
        hi_address = self.json_dict.get('address')
        hi_room_count = self.json_dict.get('room_count')
        hi_acreage = self.json_dict.get('acreage')
        hi_house_unit = self.json_dict.get('unit')
        hi_capacity = self.json_dict.get('capacity')
        hi_beds = self.json_dict.get('beds')
        hi_deposit = self.json_dict.get('deposit')
        hi_min_days = self.json_dict.get('min_days')
        hi_max_days = self.json_dict.get('max_days')
        hf_facility_id = self.json_dict.get('facility')

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
                try:
                    sql = 'delete from ih_house_info where hi_house_id=%(house_id)s'
                    self.db.execute(sql, house_id=ret)
                except Exception as e:
                    logging.error(e)
                    return self.write(dict(errcode=RET.DBERR, errmsg='fail deleting data from table ih_house_info'))
                self.write(dict(errcode=RET.DBERR, errmsg='数据库写入错误'))
            else:
                self.write(dict(errcode=RET.OK, errmsg='成功' , data=dict(houseID=ret)))

    # @require_login
    def get(self):
        '''
        :param -> house_id
               <- hi_acreage
                  hi_house_unit
                  hi_room_count
                  hi_capacity
                  hi_beds
                  hi_deposit
                  hi_min_days
                  hi_max_days
                  通过house_id在ih_house_facility中检索
        :return:
        '''
        # user_id = self.get_current_user()['userId']
        house_id = self.get_argument('id', None)
        if not house_id:
            return self.write(dict(errcode=RET.PARAMERR, errmsg='参数缺省'))

        try:
            house_detail_json = self.redis.get('houseID_%s_houseDetail'%house_id)
        except Exception as e:
            logging.error(e)
        else:
            if house_detail_json:
                house_detail = json.loads(house_detail_json)
                return self.write(dict(errcode=RET.OK, errmsg='ok', data=house_detail))
        try:
            sql = 'select up_name, up_avatar, ai_name, hi_price, hi_index_image_url, hi_address, hi_title, hi_acreage, hi_house_unit, hi_room_count, hi_capacity, hi_beds, hi_deposit, hi_min_days, hi_max_days ' \
                  'from ih_house_info inner join ih_area_info on ih_area_info.ai_area_id=ih_house_info.hi_area_id ' \
                  'inner join ih_user_profile on ih_user_profile.up_user_id=ih_house_info.hi_user_id where hi_house_id=%(house_id)s;'

            houseDetail = self.db.get(sql, house_id=house_id)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
        else:
            try:
                sql = 'select hf_facility_id from ih_house_facility where hf_house_id=%(house_id)s'
                facility = self.db.query(sql, house_id=house_id)
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
            else:
                house_detail = {}
                house_detail['user_name'] = houseDetail['up_name']
                house_detail['user_avatar'] = constants.PRE_URL + houseDetail['up_avatar']
                house_detail['address'] = houseDetail['ai_name'] + ' ' + houseDetail['hi_address']
                house_detail['title'] = houseDetail['hi_title']
                house_detail['acreage'] = houseDetail['hi_acreage']
                house_detail['unit'] = houseDetail['hi_house_unit']
                house_detail['room_count'] = houseDetail['hi_room_count']
                house_detail['capacity'] = houseDetail['hi_capacity']
                house_detail['beds'] = houseDetail['hi_beds']
                house_detail['deposit'] = houseDetail['hi_deposit']
                house_detail['min_days'] = houseDetail['hi_min_days']
                house_detail['max_days'] = houseDetail['hi_max_days']
                house_detail['index_image'] = constants.PRE_URL + houseDetail['hi_index_image_url']
                house_detail['facility'] = []
                for each in facility:
                    house_detail['facility'].append(each['hf_facility_id'])
                # 获取房屋的图片地址

                try:
                    sql = 'select hi_url from ih_house_image where hi_house_id=%(house_id)s'
                    url = self.db.query(sql, house_id=house_id)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='数据库查询出错'))
                else:
                    # 读取房屋评价
                    try:
                        sql = 'select oi_comment, up_name, oi_ctime from ih_order_info ' \
                              'inner join ih_user_profile on ih_order_info.oi_user_id=ih_user_profile.up_user_id where oi_house_id=%(house_id)s'
                        comments = self.db.query(sql, house_id=house_id)
                    except Exception as e:
                        logging.error(e)
                        self.write(dict(errcode=RET.DBERR, errmsg='评价信息查询出错'))
                    else:
                        imageList = []
                        for each in url:
                            imageList.append(constants.PRE_URL + each['hi_url'])

                        house_detail['images'] = imageList
                        house_detail['price'] = houseDetail['hi_price']
                        commentList = []
                        for each in comments:
                            innerdict = {}
                            innerdict['content'] = each['oi_comment']
                            innerdict['user_name'] = each['up_name']
                            innerdict['ctime'] = str(each['oi_ctime'])
                            commentList.append(innerdict)

                        house_detail['comments'] = commentList
                        self.write(dict(errcode=RET.OK, errmsg='ok', data=house_detail))
                        house_detail_json = json.dumps(house_detail)
                        try:
                            self.redis.setex('userID_%s_houseID_%s_houseDetail'% house_id, config.houseinfo_expire_seconds, house_detail_json)
                        except Exception as e:
                            logging.error(e)


class HouseImageHandler(BaseHandler):
    '''处理上传照片'''
    @require_login
    def post(self):
        '''
        :param 传入参数： 文件数据流写入 house-image
         url传入          house-id

        :return:
        '''
        try:
            hi_house_image = self.request.files['house_image'][0]['body']
        # 使用ajax设置url后面带参数出错
        # 這裏採用<input type='hidden'>中的value
            hi_house_id = self.get_argument('houseid')
        except:
            return self.write(dict(errcode=RET.PARAMERR, errmsg='参数缺省'))
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
        # user_id = 1
        # 房屋认证默认最长时间为一天， 我们队房屋信息进行缓存, 以减少数据库查询次数
        try:
            houseList_json = self.redis.get('userID_%s_houseinfo'%user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='redis查询出错'))
        if houseList_json:
            logging.debug('hit the redis')
            houseList = json.loads(houseList_json)
            return self.write(dict(errcode=RET.OK, errmsg='成功', data=houseList))
        try:
            sql = 'select ai_name, hi_house_id, hi_title, hi_price, hi_address, hi_ctime, hi_index_image_url from ih_house_info left join ih_area_info ' \
                  'on ih_area_info.ai_area_id = ih_house_info.hi_area_id where hi_user_id=%(user_id)s and (hi_verify_status, hi_online_status)=(2,1)'
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
                myhouse['imageUrl'] = constants.PRE_URL + each['hi_index_image_url']

                houseList.append(myhouse)

            self.write(dict(errcode=RET.OK, errmsg='成功', data=houseList))
            try:
                houseList_json = json.dumps(houseList)
                self.redis.setex('userID_%s_houseinfo'%user_id, config.houseinfo_expire_seconds, houseList_json)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errcode=RET.DBERR, errmsg='redis数据插入出错'))



class AddHouseImageHandler(BaseHandler):
    '''添加房屋照片'''
    @require_login
    @require_auth
    def post(self):
        # 限制照片上传数量
        user_id = self.get_current_user()['userId']
        try:
            pic_num = self.redis.get('%s_pic_num')
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='redis查询出错'))
        else:
            logging.debug('hit the redis')
            if pic_num > 5:
                return self.write(dict(errcode=RET.DATAEXIST, errmsg="照片数量已达上限"))

            try:
                house_id = self.get_argument('house_id')
                ImageData = self.request.files['house_image'][0]['body']
                if not all((house_id, ImageData)):
                    return self.write(dict(errcode=RET.PARAMERR, errmsg='参数缺省'))
                ImageName = storage(ImageData)
            except Exception as e:
                logging.error(e)
                self.write(dict(errcode=RET.THIRDERR, errmsg='阿里云上传出错'))
            else:
                try:
                    sql = 'insert into ih_house_image(hi_house_id, hi_url) values(%(house_id)s, %(url)s)'
                    self.db.execute(sql, house_id=house_id, url=ImageName)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='数据库查询出错'))
                else:
                    if not pic_num:
                        try:
                            sql = 'select count(hi_url) from ih_house_image group by hi_house_id;'
                            pic_num = self.db.get(sql)
                        except Exception as e:
                            logging.error(e)
                            self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
                        else:
                            try:
                                self.redis.set('%s_pic_num'%user_id, pic_num['count(hi_url)'])
                            except Exception as e:
                                logging.error(e)
                                self.write(dict(errcode=RET.DBERR, errmsg='redis数据写入错误'))
                    else:
                        pic_num += 1
                        try:
                            self.redis.set('%s_pic_num'%user_id, pic_num)
                        except Exception as e:
                            logging.error(e)
                            self.write(dict(errcode=RET.DBERR, errmsg='redis数据写入错误'))

                    url = constants.PRE_URL + ImageName
                    self.write(dict(errcode=RET.OK, errmsg='成功', data=url))


class HouseIndexHandler(BaseHandler):
    '''首页信息处理'''
    def get(self):
        '''地域信息和首页图片的查询'''
        try:
            areaList_json = self.redis.get('areaList')
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='数据查询错误'))
        else:
            if areaList_json:
                # 这里前端解析出现问题当write中为字符串时（确保json格式无误）,前端无法正常解析
                areaList = json.loads(areaList_json)
            else:
                # 从Mysql中获取ih_area_info
                try:
                    sql = 'select ai_area_id, ai_name from ih_area_info'
                    ih_area_info = self.db.query(sql)
                except Exception as e:
                    logging.error(e)
                    return self.write(dict(errcode=RET.DBERR, errmsg='数据库查询错误'))
                # ih_area_info是形如[{},{}], 中间是类字典, 需将其中数据拿出来重组
                # areaInfo = {}
                areaList = []
                for each in ih_area_info:
                    # 列表这个东西和有意思，如果在外边初始化他甚至可以修改列表前面的几项相同key值的value
                    areaInfo = {}
                    areaInfo['id'] = each['ai_area_id']
                    areaInfo['name'] = each['ai_name']
                    areaList.append(areaInfo)
                # 将areaList字符串之后以hash形式存储在redis之中
                areaList_json = json.dumps(areaList)
                try:
                    self.redis.setex('areaList', config.areainfo_expire_seconds, areaList_json)
                except Exception as e:
                    logging.error(e)
                    self.write(dict(errcode=RET.DBERR, errmsg='redis数据存储出错'))

            try:
                imagesList_json = self.redis.get('imageIndex')
            except Exception as e:
                logging.error(e)
            else:
                logging.debug('hit the redis')
                if imagesList_json:
                    imagesList = json.loads(imagesList_json)
                    dataList = dict(images=imagesList, areas=areaList)
                    return self.write(dict(errcode=RET.OK, errmsg='成功', data=dataList))
                else:
                    try:
                        sql = 'select hi_house_id, hi_index_image_url, hi_title from ih_house_info order by hi_order_count limit 3;'
                        imageinfo = self.db.query(sql)
                    except Exception as e:
                        logging.error(e)
                        return self.write(dict(errcode=RET.DBERR, errmsg='数据库查询出错'))

                    imagesList = []
                    for each in imageinfo:
                        imagesList.append(dict(image_URL=(constants.PRE_URL + each['hi_index_image_url']),
                                               house_id=each['hi_house_id'], title=each['hi_title']))

                    dataList = dict(images=imagesList, areas=areaList)
                    self.write(dict(errcode=RET.OK, errmsg='成功', data=dataList))
                    try:
                        imagesList_json = json.dumps(imagesList)
                        self.redis.set('imageIndex', config.indexinfo_expire_seconds, imagesList_json)
                    except Exception as e:
                        logging.error(e)

    def post(self):
        '''根据入住新信息和离开信息选择住房'''
        pass


class HouseListHandler(BaseHandler):
    def get(self):
        areaid = self.get_argument('aid', None)
        startDate = self.get_argument('sd', None)
        endDate = self.get_argument('ed', None)
        sortKey = self.get_argument('sk', None)
        nextpage = int(self.get_argument('p', 1))
        # 如果全为空返回最新上线的房屋信息
        sql_where = []
        sql_param = {}
        # default startDate
        if not startDate:
            startDate = datetime.datetime.now().strftime('%Y-%m-%d')
            sql_param['startDate'] = startDate
        sql_order = ''
        houses = {}
        if areaid:
            sql_areaid = 'ih_house_info.hi_area_id=%(areaid)s '
            sql_where.append(sql_areaid)
            sql_param['areaid'] = areaid

        if sortKey:
            if sortKey not in ('booking', 'price-inc', 'price-des', 'new'):
                return self.write(dict(errcode=RET.DBERR, errmsg='the sortKey not exist'))
            elif sortKey == 'booking':
                sql_order= 'order by ih_house_info.hi_room_count desc '
            elif sortKey == 'price-inc':
                sql_order = 'order by ih_house_info.hi_price '
            elif sortKey == 'new':
                sql_order = 'order by hi_ctime '
            else:
                sql_order = 'order by ih_house_info.hi_price desc '

        if startDate or endDate:
            print 'hello'
            if startDate and endDate:
                if startDate > endDate:
                    return self.write(dict(errcode=RET.DATAEXIST, errmsg='endDate must bigger than startDate'))
                else:
                    try:
                        startdate= datetime.datetime.strptime(startDate, '%Y-%m-%d')
                        enddate = datetime.datetime.strptime(endDate, '%Y-%m-%d')
                    except ValueError as e:
                        logging.error(e)
                        return self.write(dict(errcode=RET.PARAMERR, errmsg='日期格式出错'))
                    delta = (enddate - startdate).days
                    sql_param['startDate'] = startDate
                    sql_param['delta'] = str(delta)
                    print 'hello'
                    sql_where.append('hi_min_days<=%(delta)s and %(delta)s<=hi_max_days ')
            elif startDate:
                sql_param['startDate'] = startDate
            elif endDate:
                return self.write(dict(errcode=RET.OK, errmsg='succeed but no data'))

        if any((startDate, endDate, sortKey, areaid)):
            sql_sortKey = 'order by hi_ctime '
            sql_order = sql_sortKey



        sql_pre = "select distinct ih_house_info.hi_house_id, hi_index_image_url, hi_price, hi_title, hi_room_count, hi_order_count, hi_address, up_avatar, num, hi_capacity from ih_house_info left join " \
                  "(select hi_house_id, count(*)as num from ih_house_info inner join ih_order_info on ih_order_info.oi_house_id=ih_house_info.hi_house_id where %(startDate)s between oi_begin_date and oi_end_date group by hi_house_id) order_count " \
                  "on ih_house_info.hi_house_id=order_count.hi_house_id " \
                  "inner join ih_user_profile on ih_user_profile.up_user_id=ih_house_info.hi_user_id " \
                  "left join ih_order_info on ih_order_info.oi_house_id=ih_house_info.hi_house_id " \
                  "inner join ih_area_info on ih_area_info.ai_area_id = ih_house_info.hi_area_id "

        sql_where.append('(ih_house_info.hi_capacity>order_count.num ')

        sql_or = 'or num is null) '

        try:
            houses_json = self.redis.hmget('hi_%s_%s_%s_%s'%(areaid, startDate, endDate, sortKey), str(nextpage), 'total_page')
        except Exception as e:
            logging.error(e)
            houses_json = None

        if houses_json[0]:
            print 'hit the redis'
            cur_houses = json.loads(houses_json[0])
            total_page = houses_json[1]
            return self.write(dict(errcode=RET.OK, errmsg='成功', houses=cur_houses, total_page=total_page))

        sql_where = ' and '.join(sql_where)
        # 获取数据库中总数据
        try:
            sql_count_pre = "select count(distinct ih_house_info.hi_house_id) as total_num from ih_house_info left join " \
                            "(select hi_house_id, count(*) as num from ih_house_info inner join ih_order_info on ih_order_info.oi_house_id=ih_house_info.hi_house_id where %(startDate)s between oi_begin_date and oi_end_date group by hi_house_id) order_count " \
                            "on ih_house_info.hi_house_id=order_count.hi_house_id " \
                            "inner join ih_user_profile on ih_user_profile.up_user_id=ih_house_info.hi_user_id " \
                            "left join ih_order_info on ih_order_info.oi_house_id=ih_house_info.hi_house_id " \
                            "inner join ih_area_info on ih_area_info.ai_area_id = ih_house_info.hi_area_id "
            sql_count = sql_count_pre + 'where ' + sql_where + sql_or
            print sql_param
            ret_num = self.db.get(sql_count, **sql_param)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='查询总数时出错'))
        try:
            if nextpage == 1:
                sql_limit = 'limit ' + str(constants.HOUSE_LIST_CACHE_NUM * constants.HOUSE_LIST_PAGE_CAPACITY)
            else:
                sql_limit = 'limit ' + str((nextpage-1)*constants.HOUSE_LIST_PAGE_CAPACITY)+','+str(constants.HOUSE_LIST_CACHE_NUM * constants.HOUSE_LIST_PAGE_CAPACITY)
            sql = sql_pre + 'where ' + sql_where + sql_or + sql_order + sql_limit+';'
            houseInfo = self.db.query(sql, **sql_param)
            print sql_param
            logging.debug(sql)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='MySQL获取房源信息出错'))

        houselist = []
        for each in houseInfo:
            new = {}
            new['house_id'] = each['hi_house_id']
            new['image_url'] = constants.PRE_URL + each['hi_index_image_url']
            new['price'] = each['hi_price']
            new['title'] = each['hi_title']
            new['room_count'] = each['hi_room_count']
            new['order_count'] = each['hi_order_count']
            new['address'] = each['hi_address']
            new['avatar'] = constants.PRE_URL + each['up_avatar']
            new['num'] = each['num']
            new['capacity'] = each['hi_capacity']
            houselist.append(new)
            if not (houseInfo.index(each)+1)%constants.HOUSE_LIST_PAGE_CAPACITY:
                houses[houseInfo.index(each)/constants.HOUSE_LIST_PAGE_CAPACITY+nextpage] = json.dumps(houselist)
                houselist = []
                continue
        if houselist:
            houses[len(houseInfo)/constants.HOUSE_LIST_PAGE_CAPACITY+nextpage]=json.dumps(houselist)
        try:
            if not houses:
                houses[1] = json.dumps([])
                houses['total_page'] = 0
            else:
                houses['total_page'] = math.ceil(float(ret_num['total_num'])/constants.HOUSE_LIST_PAGE_CAPACITY)
            self.redis.hmset('hi_%s_%s_%s_%s'%(areaid, startDate, endDate, sortKey), houses)
        except Exception as e:
            logging.error(e)
            self.write(dict(errcode=RET.DBERR, errmsg='fail in store data of house_search'))
        else:
            try:
                self.redis.expire('house_search', config.searchinfo_expire_seconds)
            except Exception as e:
                logging.error(e)
                self.redis.delete('house_search')
        cur_houses_json = houses.get(nextpage, '[]')
        cur_houses = json.loads(cur_houses_json)
        total_page = houses.get('total_page')
        return self.write(dict(errcode=RET.OK, errmsg='成功', houses=cur_houses, total_page=total_page))







