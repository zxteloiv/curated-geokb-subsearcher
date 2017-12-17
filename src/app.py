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
        self.redirect('/statics/index.html')


class SearchHandler(tornado.web.RequestHandler):
    """Handle request to the /match route, only GET request is processed."""

    def data_received(self, chunk):
        pass

    def post(self):
        self.get()

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
        sex = self.get_argument('sex', default=None)
        age = self.get_argument('age', default=None)
        domain = self.get_argument('domain', default=None)
        city = self.get_argument('city', default=None)

        (q, now, sex, age, domain, city), fatal_err = self.normalize_params(q, now, sex, age, domain, city)
        if fatal_err is not None:
            self.write(json.dumps({"errno": 1, "errmsg": fatal_err}))
            return

        grounded = self.application.parsing_model.parse_for_mongo(q, domain=domain, city=city)
        if grounded is None:
            self.write(json.dumps({"errno":2, "errmsg":"failed to parse to grounded query"}))
            return

        mongo = MongoQuery()
        docs = mongo.coarse_query(grounded, conf.coarse_search_limit, sort_keys=[(age, -1), (sex, -1)])
        reranker = FineRanker(conf.extended_ranker)
        reranker.compute_rank_on(docs, grounded, today=now)
        docs = sorted(docs,
                      key=lambda doc: (doc['popularity'] * 100
                                       + sum(v for _, v in doc['_rerank'].iteritems())),
                      reverse=True)
        docs = mongo.project(docs, grounded, conf.finer_search_limit)

        # debug ungrounded
        # ungrounded = self.application.parsing_model._parsing_first_order_rules(
        #     self.application.parsing_model._match_keys(q))
        # ungrounded = ""

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"errno":0, "errmsg":"ok", "data":docs, "grounded":grounded, "match_score":1.}))

    @staticmethod
    def normalize_params(q, now, sex, age, domain, city):
        if not q:
            return (q, now, sex, age, domain, city), 'missing question'

        if now is not None and len(now.strip()) > 0:
            try:
                now = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M')
            except Exception:
                return (q, now, sex, age, domain, city), "time is not valid, try YYYY-mm-dd HH:MM"
        else:
            now = None

        if sex is not None and sex.strip() and sex not in ['male', 'female']:
            return (q, now, sex, age, domain, city), "sex feature is not valid, only male or female"
        if sex is not None and not sex.strip():
            sex = None

        if age is not None and age.strip() and age not in ['young', 'adult', 'elder']:
            return (q, now, sex, age, domain, city), "age feature is not valid, only young, adult or elder"
        if age is not None and not age.strip():
            age = None

        if not domain or domain not in ['tour', 'catering', 'hotel']:
            domain = None

        if not city or city not in ['beijing', 'shanghai', 'guangzhou']:
            city = None

        return (q, now, sex, age, domain, city), None


class GeoKBSearcher(tornado.web.Application):
    def __init__(self, handlers, static_path='./'):
        super(GeoKBSearcher, self).__init__(handlers,
                                            static_path=static_path,
                                            static_url_prefix="/statics/")
        self.dicts = {}
        self.dictfiles = dict((f.split('.')[0], f)
                              for f in os.listdir(conf.dict_path) if f.endswith('txt'))

    def init_dict(self):
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
        ], static_path='./statics')

    app.init_dict()
    return app


if __name__ == "__main__":
    app = make_app()
    app.listen(conf.listening_port)
    tornado.ioloop.IOLoop.current().start()

