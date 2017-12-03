# coding: utf-8
import os, os.path, json

import tornado.ioloop
import tornado.web

import conf
from parsing_model import Parsing
from mongo_model import MongoQuery
from trie import TrieIndex

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class SearchHandler(tornado.web.RequestHandler):
    """Handle request to the /match route, only GET request is processed."""
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

        if not q:
            self.write({"errno": 1, "errmsg": "parameter is missing"})
            return

        grounded = self.application.parsing_model.parse_for_mongo(q)
        if grounded is None:
            self.write(json.dumps({"errno":1, "errmsg":"failed to parse to grounded query"}))
            return

        mongo = MongoQuery()
        docs = mongo.query(grounded)

        # debug ungrounded
        ungrounded = self.application.parsing_model._parsing_first_order_rules(
                self.application.parsing_model._match_keys(q))

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"errno":0, "errmsg":"ok", "data":docs,
            "ungrounded":ungrounded, "grounded":grounded}))

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
                except:
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

