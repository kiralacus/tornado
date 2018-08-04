import datetime

nowTime = datetime.datetime.now().strftime('%Y-%m-%d')
p = datetime.datetime.strptime('2018-01-01','%Y-%m-%d')
n = datetime.datetime.strptime('2018-09-01','%Y-%m-%d')

print type(nowTime)

print (n-p).days
