#coding: utf-8
import oss2

import uuid


def storage(imageData):
    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    auth = oss2.Auth('LTAIFE7nJKyUdnoD', 'q8cT7tQHd0znxaYYwB2TQB1KBjeU4I')
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    imageName = uuid.uuid4().get_hex()+'.jpg'
    bucket = oss2.Bucket(auth, 'oss-cn-beijing.aliyuncs.com', 'kiralacus')
    bucket.put_object(imageName, imageData)
    return imageName

if __name__ == '__main__':
    f = open('/home/kiralacus/Desktop/home01.jpg', 'rb')
    imageData = f.read()
    storage(imageData)
    f.close()