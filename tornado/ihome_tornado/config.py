# coding:utf-8
import os

setting = dict(
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    cookie_secret='uffrscDURgSP6HO5m/dD52Kc2KpeBkxOpGU/5yPnTGw=',
    xsrf_cookies=False,
    debug=True,
)

mysql_option = dict(
    host='127.0.0.1',
    user='root',
    password='kiralacus',
    database='ihome',
)

redis_options = dict(
    host='127.0.0.1',
    port=6379,
)

log_level = 'debug'
log_path = os.path.join(os.path.dirname(__file__), 'logs/log')

session_expire_seconds = 86400 # session 数据有效期， 秒
areainfo_expire_seconds = 86400 # 地域信息redis数据有效期， 秒, 为了避免mysql中数据更新后redis中数据不更新
passwd_salt = 'ihome*^&'