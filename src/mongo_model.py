# coding: utf-8

from pymongo import MongoClient
import conf

class MongoQuery(object):
    def __init__(self):
        self._conn = MongoClient(conf.mongodb_conn_str)
        self._db = self._conn.geokb

    def query(self, grounded, limit=15):
        col = self._db[grounded['from']]
        docs = col.find(grounded['where'], limit=limit, sort=[('popularity', -1), ('_id', 1)])

        if '*' in grounded['select']:
            res = [dict((k, v) for k, v in doc.iteritems() if k != '_id') for doc in docs]
        else:
            res = []
            for doc in docs:
                selected = {}
                for k in grounded['select']:
                    selected[k] = doc[k]
                res.append(selected)

        return res

    def coarse_query(self, grounded, limit=2000):
        col = self._db[grounded['from']]
        docs = col.find(grounded['where'], limit=limit, sort=[('popularity', -1), ('_id', 1)])
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
                res.append(dict((k, v) for k, v in doc.iteritems() if k != '_id'))
            else:
                selected = {}
                for k in grounded['select']:
                    selected[k] = doc[k]
                res.append(selected)

        return res

