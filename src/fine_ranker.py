# coding: utf-8

import re, datetime, time

from time_ranker import TimeRanker

RANKER_BY_NAME = dict(
    TimeRanker = TimeRanker,
)

class FineRanker(object):
    def __init__(self, field_ranker_registry):
        self.registry = field_ranker_registry
        self.rankers = set(v for k, v in self.registry.iteritems())

    def compute_rank_on(self, docs, grounded, today=None):
        for doc in docs:
            doc['_rerank'] = {}
            for field, comparing_val in grounded['extended'].iteritems():
                # example data: field=营业时间, comparing_val=[("at", "现在", 1 /*matching score*/)]
                ranker_name = self.registry.get(field)
                if ranker_name is None:
                    continue

                if field not in doc:
                    doc['_rerank'][ranker_name] = 0

                ranker_cls = RANKER_BY_NAME.get(ranker_name)
                ranker = ranker_cls(doc[field])
                score = ranker.rank_against(comparing_val[0][1], today)

                doc['_rerank'][ranker_name] = score


