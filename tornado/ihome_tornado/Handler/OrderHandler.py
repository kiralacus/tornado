# coding: utf-8
from Handler.BaseHandler import BaseHandler

from utils.response_code import *

import datetime

import logging

from utils.commons import require_auth,require_login

class OrderBookHandler(BaseHandler):
    '''订单信息存储'''
    @require_login
    def post(self):
        start_date = self.json_dict.get('start_date')
        end_date = self.json_dict.get('end_date')
        house_id = self.json_dict.get('house_id')
        # user_id = 3
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
        delta = (datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date, '%Y-%m-%d')).days
        min_days = int(house['hi_min_days'])
        max_days = int(house['hi_max_days'])
        cur_orderNum = int(house['num'])
        capacity = int(house['hi_capacity'])
        price = int(house['hi_price'])
        deposit = int(house['hi_deposit'])
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
                self.db.execute(sql, user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date, house_price=price, days=delta, amount=deposit)
            except Exception as e:
                logging.error(e)
                return self.write(dict(errcode=RET.DBERR, errmsg='fail in insert data'))
            return self.write(dict(errcode=RET.OK, errmsg='成功', total_price=total_price))



