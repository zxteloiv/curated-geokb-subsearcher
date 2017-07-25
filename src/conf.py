# coding: utf-8

dict_path = "data"
listening_port = 34567
mongodb_conn_str = 'mongodb://localhost:27017'

# comparable indexes using regular expression
import re
re_comparable_index = dict(
        catering_price = [
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?(以下|以内)"), "<", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?以上"), ">", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?左右"), "~", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 3),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(低于|小于|少于|将近)(\d+)(元|块|日元)?"), "<", 3),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(低于|小于|少于|将近)(\d+)(元|块|日元)?"), "<", 3),
            (re.compile(u"(低于|小于|少于)(\d+)(元|块|日元)?"), "<", 2),
            (re.compile(u"(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 2),
            (re.compile(u"(\d+)左右"), "~", 1),
            (re.compile(u"(\d+)以下"), "<", 1),
            (re.compile(u"(\d+)以上"), ">", 1)
            ]
        )
