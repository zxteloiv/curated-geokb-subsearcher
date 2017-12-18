# coding: utf-8

dict_path = "data"
listening_port = 34567
mongodb_conn_str = 'mongodb://mongosvr:27017'

minimal_keyword_scores = dict(
    catering_dish_cond = 2,
)

coarse_search_limit = 1000
finer_search_limit = 15

# comparable indexes using regular expression
import re
re_comparable_index = dict(
        catering_price_cond = [
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?(以下|以内)"), "<+", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?以上"), ">", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)在?(\d+)(元|块|日元)?左右"), "~", 2),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 3),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(低于|小于|少于|将近|不超过)(\d+)(元|块|日元)?"), "<=+", 3),
            (re.compile(u"(人均|消费|消费水平|价格|价位)(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(低于|小于|少于)(\d+)(元|块|日元)?"), "<+", 2),
            (re.compile(u"(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 2),
            (re.compile(u"(\d+)左右"), "~", 1),
            (re.compile(u"(\d+)以下"), "<+", 1),
            (re.compile(u"(\d+)以上"), ">", 1)
            ],

        hotel_price_cond = [
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?(以下|以内)"), "<+", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?以上"), ">", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?左右"), "~", 2),
            (re.compile(u"(价格|价位)(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 3),
            (re.compile(u"(价格|价位)(低于|小于|少于|将近|不超过)(\d+)(元|块|日元)?"), "<=+", 3),
            (re.compile(u"(价格|价位)(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(低于|小于|少于)(\d+)(元|块|日元)?"), "<+", 2),
            (re.compile(u"(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 2),
            (re.compile(u"(\d+)左右"), "~", 1),
            (re.compile(u"(\d+)以下"), "<+", 1),
            (re.compile(u"(\d+)以上"), ">", 1)
            ],

        tour_price_cond = [
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?(以下|以内)"), "<+", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?以上"), ">", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(价格|价位)在?(\d+)(元|块|日元)?左右"), "~", 2),
            (re.compile(u"(价格|价位)(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 3),
            (re.compile(u"(价格|价位)(低于|小于|少于|将近|不超过)(\d+)(元|块|日元)?"), "<=+", 3),
            (re.compile(u"(价格|价位)(\d+)(元|块|日元)?"), "=", 2),
            (re.compile(u"(低于|小于|少于)(\d+)(元|块|日元)?"), "<+", 2),
            (re.compile(u"(高于|大于|多于)(\d+)(元|块|日元)?"), ">", 2),
            (re.compile(u"(\d+)左右"), "~", 1),
            (re.compile(u"(\d+)以下"), "<+", 1),
            (re.compile(u"(\d+)以上"), ">", 1)
            ],
        )

# index here can be used as a query condition, all other index are only for interrogation.
# this could help predict the query schema, using only available conditions
conditionable_index = dict(
        # the sequence order in each domain is meaningful, the former ones, the higher exclusive priority
        catering = ['price_cond', 'entity', 'dish_cond'],
        hotel = ['price_cond', 'entity', 'hotel_facility_cond', 'room_facility_cond', 'hotel_service_cond'],
        tour = ['price_cond', 'entity']
        )

extended_match_index = dict(
    catering_opening_hour_cond = [
        (re.compile(u"(现在|今天)(开门|营业)"),
         "at", 1),

        (re.compile(u"((节假日|工作日|周[一二三四五六日]|周末|今天)?(早上|下午|晚上|半夜)?\d+点).?(开门|营业)"),
         "at", 1),

        (re.compile(u"((早上|下午|晚上|半夜)([一二三四五六七八九十\d]|十一|十二|1[012])点).?(开门|营业)"),
         "at", 1),
    ],

    tour_opening_hour_cond = [
        (re.compile(u"(现在|今天)(开门|营业)"),
         "at", 1),

        (re.compile(u"((节假日|工作日|周[一二三四五六日]|周末|今天)?(早上|下午|晚上|半夜)?\d+点).?(开门|营业)"),
         "at", 1),

        (re.compile(u"((早上|下午|晚上|半夜)([一二三四五六七八九十\d]|十一|十二|1[012])点).?(开门|营业)"),
         "at", 1),
    ],
)

extendable_index = dict(
    catering = ['opening_hour_cond'],
    tour = ['opening_hour_cond'],
    hotel = [],
)

extended_ranker = {
    u'营业时间': 'TimeRanker',
}

mongo_comparison_spec = dict(

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
            u'名称': ('=', 'prop', u'名称'),
            u'推荐菜品': ('=', 'nested', u'推荐菜品.推荐菜'),
            u'电话': ('=', 'prop', u'电话'),
            u'人均消费': ('compare', 'prop', u'人均消费'),
            #u'营业时间': ('compare', 'prop', ''), # not supported as a condition yet
            #u'地址': ('contains', 'prop', u'地址'),
            },

        hotel = {
            u'名称': ('=', 'prop', u'名称'),
            u'联系方式': ('=', 'prop', u'联系方式'),
            u'每晚最低价格': ('compare', 'prop', u'每晚最低价格'),
            u'酒店设施': ('=', 'nested', u'酒店设施.设施'),
            u'房间设施': ('=', 'nested', u'房间设施.设施'),
            u'酒店服务': ('=', 'nested', u'酒店服务.服务'),
            #u'入离店时间': ('compare', 'prop', ''), # not supported as a condition yet
            #u'地址': ('contains', 'prop', u'地址'),
            },

        tour = {
            u'名称': ('=', 'prop', u'名称'),
            u'电话': ('=', 'prop', u'电话'),
            u'门票价格': ('compare', 'prop', u'门票价格'),
            #u'营业时间': ('compare', 'prop', ''), # not supported as a condition yet
            #u'地址': ('contains', 'prop', u'地址'),
            },

        )

mongo_grounding_map = dict(

        domain_map = {'catering': 'cater', 'tour': 'tour', 'hotel': 'hotel'},

        city_map = {
            u'广州': 'guangzhou', u'北京': 'beijing', u'上海': 'shanghai',
            'guangzhou': 'guangzhou', 'beijing': 'beijing', 'shanghai': 'shanghai',
        },

        # map an ungrounded key to a grouned one
        field_map = {
            'cater': {
                # interrogative ungrounded keys
                'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                'dish': u'推荐菜品', 'phone': u'电话', 'price': u'人均消费', 'opening_hour': u'营业时间',

                # special ungrounded keys
                'popularity': u'popularity',
                'opening_hour_cond': u'营业时间',

                # conditionable ungrounded keys
                'price_cond': u'人均消费', 'dish_cond': u'推荐菜品',
                },

            'hotel': {
                # interrogative ungrounded keys
                'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                'check-in_time': u'入离店时间', 'phone': u'联系方式', 'price_per_night': u'每晚最低价格',
                'hotel_facility': u'酒店设施', 'room_facility': u'房间设施', 'hotel_service': u'酒店服务',

                # special ungrounded keys
                'popularity': u'popularity',

                # conditionable ungrounded keys
                'price_cond': u'每晚最低价格', 'hotel_facility_cond': u'酒店设施',
                'room_facility_cond': u'房间设施', 'hotel_service_cond': u'酒店服务',
                },

            'tour': {
                # interrogative ungrounded keys
                'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                'opening_hour': u'营业时间', 'phone': u'电话', 'price': u'门票价格',

                # special ungrounded keys
                'popularity': u'popularity',
                'opening_hour_cond': u'营业时间',

                # conditionable ungrounded keys
                'price_cond': u'门票价格',
                },
            }

        )

