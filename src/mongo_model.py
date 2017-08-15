# coding: utf-8

from pymongo import MongoClient
import conf

class MongoQuery(object):
    def __init__(self):
        self._conn = MongoClient(conf.mongodb_conn_str)
        self._db = self._conn.geokb

    def query(self, grounded, limit=15):
        col = self._db[grounded['from']]
        docs = col.find(grounded['where'], limit=limit)

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
