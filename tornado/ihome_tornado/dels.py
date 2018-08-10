import datetime
import math
import json

# test = "[{'house_id': 2L, 'order_count': 3L, 'price': 100L, 'title': u'\u5bb6\u4e00\u53f7', 'num': 2L, 'room_count': 2, 'image_url': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/8772b66a8da4457c891674bbf11b7e48.jpg', 'avatar': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/bf94f713816d4fafa3c5d334aa3318c1.jpg', 'address': u'\u5929\u4e0a\u4eba\u95f4\u4e00\u53f7', 'capacity': 3L}, {'house_id': 3L, 'order_count': 2L, 'price': 200L, 'title': u'\u4e8c\u53f7\u5bb6', 'num': None, 'room_count': 3, 'image_url': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/589ba92b7afb42b0b4028f60d1a966d0.jpg', 'avatar': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/bf94f713816d4fafa3c5d334aa3318c1.jpg', 'address': u'\u5929\u4e0a\u4eba\u95f42\u53f7', 'capacity': 2L}, {'house_id': 4L, 'order_count': 1L, 'price': 300L, 'title': u'\u4e09\u53f7\u5bb6', 'num': None, 'room_count': 3, 'image_url': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/995d927cccf04f6cad78fb995f578dad.jpg', 'avatar': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/bf94f713816d4fafa3c5d334aa3318c1.jpg', 'address': u'\u5929\u4e0a\u4eba\u95f43\u53f7', 'capacity': 3L}]", '2': "[{'house_id': 5L, 'order_count': 0L, 'price': 400L, 'title': u'\u5bb6\u56db\u53f7', 'num': None, 'room_count': 4, 'image_url': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/e7f268a23e1042e3b486392870c483bf.jpg', 'avatar': u'https://kiralacus.oss-cn-beijing.aliyuncs.com/bf94f713816d4fafa3c5d334aa3318c1.jpg', 'address': u'\u5929\u4e0a\u4eba\u95f44\u53f7', 'capacity': 4L}]"
# print type(json.loads(test))
test = "[{'name':'kira'}]"
# t = {'1': 'kira'}
# print json.loads(test)
t = json.dumps(test)
print t
print type(json.loads(t))
# print type(json.loads(t))


