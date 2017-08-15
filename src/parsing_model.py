# coding: utf-8

import conf
from substring import substring_iter

class Parsing(object):
    def __init__(self, dicts):
        self._dicts = dicts
        self._domain_map = {'catering': 'cater', 'tour': 'tour', 'hotel': 'hotel'}
        self._city_map = {u'广州': 'guangzhou', u'北京': 'beijing', u'上海': 'shanghai'}
        self._field_map = {
                'cater': {
                    'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                    'dish': u'推荐菜品', 'phone': u'电话', 'price': u'人均消费', 'opening_hour': u'营业时间',
                    },
                'hotel': {
                    'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                    'check-in_time': u'入离店时间', 'phone': u'联系方式', 'price_per_night': u'每晚最低价格',
                    'hotel_facility': u'酒店设施', 'room_facility': u'房间设施', 'service': u'酒店服务'
                    },
                'tour': {
                    'address': u'地址', 'category': u'领域', 'entity': u'名称', 'location': u'地点',
                    'opening_hour': u'营业时间', 'phone': u'电话', 'price': u'门票价格'
                    },
                }

    def parse_for_mongo(self, u_q):
        matched_keys = self._match_keys(u_q)
        ungrounded_form = self._parsing_first_order_rules(matched_keys)
        if ungrounded_form is None:
            return

        grounded = self._make_grounded_query(ungrounded_form)
        if grounded is None:
            return

        return grounded

    def _match_keys(self, u_q):
        matched_keys = {}
        dicts = self._dicts

        # exact match for substring
        for substring in substring_iter(u_q, min_len=2):
            if len(substring) > 10: continue

            for index in dicts.iterkeys():
                score = dicts[index].get(substring)
                if score is None: continue

                if (index not in matched_keys) or (
                    score > matched_keys[index][2]) or (
                    score == matched_keys[index][2] and len(substring) > len(matched_keys[index][1])):
                    matched_keys[index] = ('=', substring, score)

        # reg exp on the whole sentence
        index = 'catering_price'
        rulelist = conf.re_comparable_index[index]
        for (patobj, sym, groupid) in rulelist:
            m = patobj.search(u_q)
            if m:
                matched_keys[index] = (sym, float(m.group(groupid)), 1)
                break

        return matched_keys

    def _make_grounded_query(self, ungrounded_form):
        grounded = {}

        uf_from = ungrounded_form['from']
        domain, city = self._domain_map.get(uf_from[0]), self._city_map.get(uf_from[1])
        if domain is None or city is None:
            return None
        grounded['from'] = city + '_' + domain

        grounded['select'] = [self._field_map[domain].get(x) for x in ungrounded_form['select']]
        if None in grounded['select']:
            return None
        if len(ungrounded_form['select']) == 1 and 'entity' in ungrounded_form['select']:
            grounded['select'].append('*')

        grounded['where'] = {}
        db_condition = conf.mongo_grounded_index_condition.get(domain)
        if db_condition is None: return None

        for (key, (sym, val, score)) in ungrounded_form['where'].iteritems():
            key_support = db_condition.get(self._field_map[domain].get(key))
            if key_support is None: return None
            comp_type, _, field = key_support

            if sym == '=':
                grounded['where'][field] = val
            elif sym == '>':
                grounded['where'][field] = {'$gt': val}
            elif sym == '<':
                grounded['where'][field] = {'$lt': val}
            else:
                pass

        return grounded

    def _parsing_first_order_rules(self, matched_keys):
        # example of matched_keys:
        # ["tour_entity", ["基督教天河堂", 1.0]], ["catering_location", ["广州", 656.0]]
        domain = self._parse_domain(matched_keys)
        if domain is None: return None
        city = self._parse_city(domain, matched_keys)
        if city is None: return None

        # filter the matches for the specific domain, and remove domain prefix for all keys
        domain_match = dict((k[(k.find('_') + 1):], v) for k, v in matched_keys.iteritems()
                if domain in k and 'category' not in k and 'location' not in k)

        ungrounded_form = self._build_unground_form(domain, city, domain_match)

        return ungrounded_form

    def _build_unground_form(self, domain, city, domain_match):
        ungrounded_form = {'where': {}, 'select': [], 'from': [domain, city]}

        # entity is a dominate key
        if 'entity' in domain_match.keys():
            ungrounded_form['where'] = {'entity': domain_match['entity']}
            ungrounded_form['select'] = [k for k in domain_match.iterkeys() if k != 'entity']
            return ungrounded_form

        ungrounded_form['select'] = ['entity']
        ungrounded_form['where'] = domain_match

        return ungrounded_form

    def _parse_city(self, domain, matched_keys):
        city_pair = matched_keys.get(domain + '_location')
        if city_pair is not None:
            return city_pair[1]

        # additional rules to extract city can be added here in the future
        return None

    def _parse_domain(self, matched_keys):
        category_keys = [key for key in matched_keys.iterkeys() if 'category' in key]
        key_to_domain = lambda key: key.split('_')[0]
        choose_best_key_by_score = lambda l: max(l, key=lambda x: matched_keys[x][2])

        if len(category_keys) >= 1:
            # choose the one with HIGHEST SCORE among candidates
            best_key = choose_best_key_by_score(category_keys)
            return key_to_domain(best_key)

        # no category keys explicitly found, use the entity type
        entity_keys = [key for key in matched_keys.iterkeys() if 'entity' in key]
        if len(entity_keys) >= 1:
            best_key = choose_best_key_by_score(entity_keys)
            return key_to_domain(best_key)

        # no other features
        return None


