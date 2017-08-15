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

mongo_grounded_index_condition = dict(

        # configs are listed as K:V pairs categorized by each domain,
        # where K is a realistic key name in mongo
        # and V is a triple
        # whose elements meanings are, respectively,
        #   1. how value comparison is supported according to this key,
        #       contains: database value can contain the text in query
        #              =: database value must be equal to the value in query
        #        compare: database value is a comparable to a given number
        #   2. what a value is stored actually in mongodb
        #           prop: the specified value is a bare key in db, compare with it directly
        #         nested: the specified value is contained in a nested document
        #   3. the actual comparable key name in database.
        #      if the value is nested, this field contains the actual nested property selector

        cater = {
            u'地址': ('contains', 'prop', u'地址'),
            u'名称': ('=', 'prop', u'名称'),
            u'推荐菜品': ('=', 'nested', u'推荐菜品.推荐菜'),
            u'电话': ('=', 'prop', u'电话'),
            u'人均消费': ('compare', 'prop', u'人均消费'),
            #u'营业时间': ('compare', 'prop', ''), # not supported as a condition yet
            },

        hotel = {
            u'地址': ('contains', 'prop', u'地址'),
            u'名称': ('=', 'prop', u'名称'),
            u'联系方式': ('=', 'prop', u'联系方式'),
            u'每晚最低价格': ('compare', 'prop', u'每晚最低价格'),
            u'酒店设施': ('=', 'nested', u'酒店设施.设施'),
            u'房间设施': ('=', 'nested', u'房间设施.设施'),
            u'酒店服务': ('=', 'nested', u'酒店服务.服务'),
            #u'入离店时间': ('compare', 'prop', ''), # not supported as a condition yet
            },

        tour = {
            u'地址': ('contains', 'prop', u'地址'),
            u'名称': ('=', 'prop', u'名称'),
            u'电话': ('=', 'prop', u'电话'),
            u'门票价格': ('compare', 'prop', u'门票价格'),
            #u'营业时间': ('compare', 'prop', ''), # not supported as a condition yet
            },

        )
