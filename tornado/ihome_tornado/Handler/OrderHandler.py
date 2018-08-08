# coding: utf-8
from Handler.BaseHandler import BaseHandler

from utils.response_code import *

import datetime

import logging

from utils.commons import require_login, require_auth

class BookOrderHandler(BaseHandler):
    '''订单信息存储'''
    @require_login
    def post(self):
        start_date = self.json_dict.get('start_date')
        end_date = self.json_dict.get('end_date')
        house_id = self.json_dict.get('house_id')
        user_id = self.get_current_user().get('userId')
        if not all((start_date, end_date, house_id)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg='miss the param'))
        if start_date > end_date:
            return self.write(dict(errcode=RET.DATAEXIST, errmsg='start_date must be smaller'))
        # 获取房屋信息
        try:
            sql = 'select hi_deposit, hi_price, hi_max_days, hi_min_days, hi_capacity, num from ih_house_info ' \
                  'right join (select count(*) as num, oi_house_id from ih_order_info where %(start_date)s between oi_begin_date and oi_end_date and oi_house_id=%(house_id)s group by oi_house_id) t ' \
                  'on t.oi_house_id=ih_house_info.hi_house_id;'
            house = self.db.get(sql, start_date=start_date, house_id=house_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='获取房屋信息出错'))
        delta = ((datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date, '%Y-%m-%d')).days)+1
        min_days = int(house['hi_min_days'])
        max_days = int(house['hi_max_days'])
        cur_orderNum = int(house['num'])
        capacity = int(house['hi_capacity'])
        price = int(house['hi_price'])
        amount = price*delta
        if not(delta >= min_days and delta <= max_days):
            if delta < min_days:
                return self.write(dict(errcode=RET.DATAERR, errmsg='住房时间过短'))
            elif delta > max_days:
                return self.write(dict(errcode=RET.DATAERR, errmsg='住房时间过长'))
        elif cur_orderNum >= capacity:
            return self.write(dict(errcode=RET.DATAERR, errmsg='房屋居住人数已满'))
        else:
            total_price = price * float(delta)
            try:
                sql = 'insert into ih_order_info(oi_user_id, oi_house_id, oi_begin_date, oi_end_date, oi_days, oi_house_price, oi_amount)' \
                      'values(%(user_id)s, %(house_id)s, %(begin_date)s, %(end_date)s, %(days)s, %(house_price)s, %(amount)s);'
                self.db.execute(sql, user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date, house_price=price, days=delta, amount=amount)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errcode=RET.DBERR, errmsg='fail in insert data'))
            return self.write(dict(errcode=RET.OK, errmsg='成功', total_price=total_price))


class MyOrderHandler(BaseHandler):
    '''處理我的訂單內容'''
    @require_login
    def get(self):
        '''
        :return:
        param 1.order_id 2.order_status 3.image_url 4.order_title 5.order_ctime 6.order_start_date 7.order_end_date 8.order_amount 9.order_days 10. order_comment
        '''
        user_id = self.get_current_user().get('userId')
        try:
            sql = 'select oi_order_id, oi_begin_date, oi_status, oi_end_date, oi_days, oi_ctime, oi_house_price, hi_title, hi_index_image_url, oi_comment from ih_order_info ' \
                  'inner join ih_house_info on ih_order_info.oi_house_id = ih_house_info.hi_house_id where oi_user_id=%(user_id)s'
            order_info = self.db.query(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='数据库查询订单信息出错'))
        order = []
        for each in order_info:
            order_dict = {}
            order_dict['order_id'] = each['oi_order_id']
            order_dict['start_date'] = str(each['oi_begin_date'])
            order_dict['end_date'] = str(each['oi_end_date'])
            order_dict['status'] = each['oi_status']
            order_dict['ctime'] = str(each['oi_ctime'])
            order_dict['days'] = each['oi_days']
            order_dict['title'] = each['hi_title']
            order_dict['img_url'] = each['hi_index_image_url']
            order_dict['amount'] = each['oi_house_price']
            order_dict['comment'] = each['oi_comment']
            order.append(order_dict)
        print order
        return self.write(dict(errcode=RET.OK, errmsg='成功', order=order))

    def post(self):
        '''提交评论内容'''
        order_id = self.json_dict.get('order_id')
        comment = self.json_dict.get('comment')
        if not all((comment, order_id)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg='缺少参数'))
        if len(comment) <= 5:
            return self.write(dict(errcode=RET.PARAMERR, errmsg='评论字数必须大于５'))
        try:
            sql = 'update ih_order_info set oi_comment=%(comment)s where oi_order_id=%(order_id)s'
            self.db.execute(sql, comment=comment, order_id=order_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='向数据库写入数据出错'))
        return self.write(dict(errcode=RET.OK, errmsg='成功'))

class GuestOrderHandler(BaseHandler):
    @require_login
    @require_auth
    def get(self):
        '''
        oi_order_id-> order_id
        oi_status -> status
        hi_title -> title
        oi_ctime -> ctime
        oi_begin_date -> begin_date
        oi_end_date -> end_date
        oi_amount -> amount
        oi_days -> days
        oi_comment -> comment
        :return:

        '''
        user_id = self.get_current_user().get('userId')
        # user_id = 1
        try:
            sql = 'select oi_order_id, oi_status, hi_title, oi_ctime, oi_begin_date, oi_end_date, oi_amount, oi_days, oi_comment from ih_house_info ' \
                  'inner join ih_order_info on ih_order_info.oi_house_id=ih_house_info.hi_house_id where hi_user_id=%(user_id)s;'
            order_info = self.db.query(sql, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='订单数据查询错误'))

        order = []
        for each in order_info:
            order_dict = {}
            order_dict['order_id'] = each['oi_order_id']
            order_dict['status'] = each['oi_status']
            order_dict['title'] = each['hi_title']
            order_dict['ctime'] = str(each['oi_ctime'])
            order_dict['begin_date'] = str(each['oi_begin_date'])
            order_dict['end_date'] = str(each['oi_end_date'])
            order_dict['amount'] = each['oi_amount']
            order_dict['days'] = each['oi_days']
            order_dict['comment'] = each['oi_comment']
            order.append(order_dict)

        return self.write(dict(errcode=RET.OK, errmsg='成功', order=order))

    def post(self):
        order_id = self.json_dict.get('order_id')
        comment = self.json_dict.get('comment')
        if not all((order_id, comment)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg='缺少参数'))
        try:
            sql = 'update ih_order_info set oi_comment=%(comment)s where oi_order_id=%(order_id)s'
            self.db.execute(sql, order_id=order_id, comment=comment)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errcode=RET.DBERR, errmsg='数据库写入失败'))
        return self.write(dict(errcode=RET.OK, errmsg='成功'))



















