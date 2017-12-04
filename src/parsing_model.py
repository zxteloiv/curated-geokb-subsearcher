# coding: utf-8

import conf
from substring import substring_iter

class Parsing(object):
    def __init__(self, dicts):
        self._dicts = dicts

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

        # overlap checking, a span shall not be overlappingly used
        pos_overlap_check = []

        # extended special matching
        for index, rulelist in conf.extended_match_index.iteritems():
            for (patobj, sym, groupid) in rulelist:
                m = patobj.search(u_q)
                if m:
                    matched_keys[index] = [(sym, m.group(groupid), 1)]
                    pos_overlap_check.append(m.span())
                    break

        # reg exp on the whole sentence, all kinds of comparable keys
        for index, rulelist in conf.re_comparable_index.iteritems():
            for (patobj, sym, groupid) in rulelist:
                m = patobj.search(u_q)
                if m:
                    span = m.span()
                    if not(all(span[1] <= s[0] or span[0] >= s[1] for s in pos_overlap_check)):
                        continue

                    matched_keys[index] = [(sym, float(m.group(groupid)), 1)]
                    pos_overlap_check.append(m.span())
                    break

        # exact match for substring
        for substring, span in substring_iter(u_q, min_len=2):
            if len(substring) > 15: continue
            if not(all(span[1] <= s[0] or span[0] >= s[1] for s in pos_overlap_check)):
                continue

            for index in dicts.iterkeys():
                score = dicts[index].get(substring)
                if score is None: continue

                if index in conf.minimal_keyword_scores and float(score) < conf.minimal_keyword_scores[index]:
                    continue

                if index not in matched_keys:
                    matched_keys[index] = []

                # save all the possible matches as a list
                matched_keys[index].append(('=', substring.strip(), score))

        return matched_keys

    def _parsing_first_order_rules(self, matched_keys):
        # example of matched_keys:
        # ["tour_entity", ["基督教天河堂", 1.0]], ["catering_location", ["广州", 656.0]]
        domain = self._parse_domain(matched_keys)
        if domain is None: return None
        city = self._parse_city(domain, matched_keys)
        if city is None: return None

        # filter the matches for the specific domain, and remove domain prefix for all keys
        in_domain_match = dict((k[(k.find('_') + 1):], v) for k, v in matched_keys.iteritems()
                if domain in k and 'category' not in k and 'location' not in k)

        ungrounded_form = self._build_unground_form(domain, city, in_domain_match)

        return ungrounded_form

    def _build_unground_form(self, domain, city, in_domain_match):
        ungrounded_form = {'where': {}, 'select': [], 'from': [domain, city], 'extended': {}}

        # predict query structure depending on the matched key types
        matched_keys = set(in_domain_match.keys())

        # check the conditionable keys
        condition_keys = conf.conditionable_index[domain]
        for k in condition_keys:
            if k not in matched_keys: continue
            if not ungrounded_form['where']:
                ungrounded_form['where'][k] = in_domain_match[k]
            #     ungrounded_form['select'].append(k)
            # matched_keys.remove(k)

        # all the conditioning keys are used in selection
        ungrounded_form['select'].extend(list(matched_keys))

        for k in conf.extended_match_index.iterkeys():
            if k in matched_keys:
                ungrounded_form[k] = in_domain_match[k]
                if k in ungrounded_form['where']:
                    del ungrounded_form['where'][k]

        return ungrounded_form

    @staticmethod
    def _best_triple_by_score(self, matched_keys, key):
        # matched keys contains: K, V pairs
        # K is a string
        # V is a list of triples: (symbol, value, score)
        if key not in matched_keys:
            return None

        best_triple = max(matched_keys[key], key=lambda x: x[2]) 
        return best_triple

    def _parse_city(self, domain, matched_keys):
        city_triple = self._best_triple_by_score(matched_keys, domain + '_location')
        if city_triple is not None:
            return city_triple[1]

        # additional rules to extract city can be added here in the future
        return None

    def _parse_domain(self, matched_keys):
        category_keys = [key for key in matched_keys.iterkeys() if 'category' in key]
        key_to_domain = lambda key: key.split('_')[0]
        choose_best_key_by_best_score = (
            lambda l: max(l, key=lambda x: self._best_triple_by_score(matched_keys, x)[2]))

        if len(category_keys) >= 1:
            # choose the one with HIGHEST SCORE among candidates
            best_key = choose_best_key_by_best_score(category_keys)
            return key_to_domain(best_key)

        # no category keys explicitly found, use the entity type
        entity_keys = [key for key in matched_keys.iterkeys() if 'entity' in key]
        if len(entity_keys) >= 1:
            best_key = choose_best_key_by_best_score(entity_keys)
            return key_to_domain(best_key)

        # no other features
        return None

    def _make_grounded_query(self, ungrounded_form):
        grounded = {}

        domain_map = conf.mongo_grounding_map['domain_map']
        city_map = conf.mongo_grounding_map['city_map']
        field_map = conf.mongo_grounding_map['field_map']

        # ground-ing `from` section
        uf_from = ungrounded_form['from']
        domain, city = domain_map.get(uf_from[0]), city_map.get(uf_from[1])
        if domain is None or city is None:
            return None
        grounded['from'] = city + '_' + domain

        # ground-ing `select` section
        grounded['select'] = [field_map[domain].get(x) for x in ungrounded_form['select']]
        if None in grounded['select']: # which means there's invalid index name in the ungrounded_form
            return None

        # ground-ing `extended` section, which is simple because we do not rely on the mongo engine
        # grounded['extended'] = [field_map[domain].get(x[0]) for x in ungrounded_form['select']]
        # if None in grounded['extended']:
        #     return None

        # make sure the basic fields are exists within grounded forms: entity_name, address, or everything
        if len(ungrounded_form['select']) == 1 and 'entity' in ungrounded_form['select']:
            grounded['select'].append('*')
        else:
            grounded['select'].extend(field_map[domain][x] for x in ['entity', 'address', 'popularity'])
            grounded['select'] = list(set(grounded['select']))

        # ground-ing `where` section
        grounded['where'] = {}
        comp_spec = conf.mongo_comparison_spec.get(domain)
        if comp_spec is None: return None

        for (key, possible_matches) in ungrounded_form['where'].iteritems():
            # possible_matches is [ (sym, val, score), ... ], namely a triple list
            # if comparison type is =, then any value "$in" triple list is possible
            # if comparison type is compare

            key_comp_spec = comp_spec.get(field_map[domain].get(key))
            if key_comp_spec is None: return None
            comp_type, _, field = key_comp_spec

            if comp_type == '=':
                grounded['where'][field] = {'$in': [val for _, val, _ in possible_matches]}
            elif comp_type == 'compare':
                grounded['where'][field] = {}
                for triple in possible_matches:
                    grounded_cond = self._ground_a_comparing_triple(triple, field)
                    grounded['where'][field].update(grounded_cond)

        return grounded

    def _ground_a_comparing_triple(self, triple, field):
        sym, val, score = triple
        if sym == '=':
            return {'$eq': val}
        elif sym == '>':
            return {'$gt': val}
        elif sym == '<':
            return {'$lt': val}
        elif sym == '<=':
            return {'$lte': val}
        elif sym == '<+':
            return {'$lt': val, '$gt': 0}
        elif sym == '<=+':
            return {'$lte': val, '$gt': 0}
        else:
            pass
        return {}


