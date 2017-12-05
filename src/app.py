# coding: utf-8
import os, os.path, json, datetime

import tornado.ioloop
import tornado.web

import conf
from parsing_model import Parsing
from mongo_model import MongoQuery
import fine_ranker
from trie import TrieIndex
FineRanker = fine_ranker.FineRanker


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class SearchHandler(tornado.web.RequestHandler):
    """Handle request to the /match route, only GET request is processed."""

    def data_received(self, chunk):
        pass

    def get(self):
        """Process the GET request.

        GET Args (all are converted to unicode):
            q (str): question string in utf-8 which must be url encoded

        Return (dict in json):
            errno (int): 0 if success, otherwise other error numbers
            errmsg (str): "ok" if success, otherwise other error messages
            data (list): 
        """
        q = self.get_argument('q', default=None)
        now = self.get_argument('time', default=None)

        if not q:
            self.write({"errno": 1, "errmsg": "parameter is missing"})
            return

        if now is not None:
            try:
                now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M')
            except Exception:
                self.write({"errno": 1, "errmsg": "time is not valid, try YYYY-mm-dd HH:MM"})
                return

        grounded = self.application.parsing_model.parse_for_mongo(q)
        if grounded is None:
            self.write(json.dumps({"errno":1, "errmsg":"failed to parse to grounded query"}))
            return

        mongo = MongoQuery()
        docs = mongo.coarse_query(grounded, conf.coarse_search_limit)
        reranker = FineRanker(conf.extended_ranker)
        reranker.compute_rank_on(docs, grounded, today=now)
        docs = sorted(docs,
                      key=lambda doc: doc['popularity'] * 100 + sum(v for _, v in doc['_rerank'].iteritems()),
                      reverse=True)
        docs = mongo.project(docs, grounded, conf.finer_search_limit)

        # debug ungrounded
        # ungrounded = self.application.parsing_model._parsing_first_order_rules(
        #     self.application.parsing_model._match_keys(q))
        # ungrounded = ""

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"errno":0, "errmsg":"ok", "data":docs, "grounded":grounded}))


class GeoKBSearcher(tornado.web.Application):
    def init_dict(self):
        self.dicts = {}
        self.dictfiles = dict((f.split('.')[0], f) 
                              for f in os.listdir(conf.dict_path) if f.endswith('txt'))

        for f_tag, f in self.dictfiles.iteritems():
            findex = TrieIndex()
            for line in open(os.path.join(conf.dict_path, f)):
                parts = line.decode('utf-8').rstrip().split('\t')
                try:
                    findex.add(parts[0], float(parts[1]))
                except Exception:
                    print "errline:", line.rstrip()
                    continue

            self.dicts[f_tag] = findex

        self.parsing_model = Parsing(self.dicts)


def make_app():
    app = GeoKBSearcher([
        (r"/", MainHandler),
        (r"/s", SearchHandler),
        ])

    app.init_dict()
    return app


if __name__ == "__main__":
    app = make_app()
    app.listen(conf.listening_port)
    tornado.ioloop.IOLoop.current().start()

