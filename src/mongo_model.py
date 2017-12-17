# coding: utf-8

from pymongo import MongoClient
import conf

class MongoQuery(object):
    def __init__(self):
        self._conn = MongoClient(conf.mongodb_conn_str)
        self._db = self._conn.geokb

    def query(self, grounded, limit=15, sort_keys=None):
        col = self._db[grounded['from']]
        docs = col.find(grounded['where'],
                        limit=limit,
                        sort=([('popularity', -1)]
                              + ['_sys_ranks.%s' % x[0] for x in sort_keys if x is not None])
                        )

        if '*' in grounded['select']:
            res = [dict((k, v) for k, v in doc.iteritems() if k != '_id') for doc in docs]
        else:
            res = []
            for doc in docs:
                selected = {}
                for k in grounded['select']:
                    if k in doc:
                        selected[k] = doc[k]
                res.append(selected)

        return res

    def coarse_query(self, grounded, limit=2000, sort_keys=None):
        col = self._db[grounded['from']]
        # docs = col.find(grounded['where'], limit=limit, sort=[('popularity', -1), ('_id', 1)])
        docs = col.find(grounded['where'],
                        limit=limit,
                        sort=([('popularity', -1)]
                              + [('_sys_ranks.%s' % x[0], -1) for x in sort_keys if x is not None])
                        )
        return [dict((k, v) for k, v in doc.iteritems() if k != '_id') for doc in docs]

    def project(self, docs, grounded, limit=15):
        res = []
        for doc in docs:
            if len(res) >= 15:
                break

            try:
                score = doc['_rerank']['TimeRanker']
                if score < 1:
                    continue
            except KeyError:
                pass

            if '*' in grounded['select']:
                doc = dict((k, v) if type(v) != type([]) else (k, self._merge_obj_array(v))
                        for k, v in doc.iteritems() if k != '_id')
                doc['src'] = 'geokb'
                doc['score'] = 2.0  # fixed high score for nginx blender, in another module
                res.append(doc)
            else:
                selected = {}
                for k in grounded['select']:
                    if type(doc[k]) == type([]):
                        selected[k] = self._merge_obj_array(doc[k])
                    else:
                        selected[k] = doc[k]
                selected['_sys_ranks'] = doc['_sys_ranks']
                selected['src'] = 'geokb'
                selected['score'] = 2.0  # fixed high score for nginx blender, in another module
                res.append(selected)

        return res

    @staticmethod
    def _merge_obj_array(arr):
        if len(arr) == 0 or type(arr) != type([]):
            return arr

        if type(arr[0]) != type(dict()):
            return arr

        # [{u'推荐菜': u'AA"}, {u'推荐菜': u'BB'}, ...]
        get_val_lst = lambda o: [v for _, v in o.iteritems()]
        lst = []
        for obj in arr:
            lst += get_val_lst(obj)

        return lst


