#coding: utf-8
import oss2

import uuid

import json


test = {'name': 'kira'}


l = [1,2,3]
sql = 'insert into ih_house_facility(hf_house_id, hf_facility_id) values'
for each in l:
    afsql = '(%s, %s)'%(1, each) + ','
    sql += afsql

print sql.rstrip(',')

