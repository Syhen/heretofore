# -*- coding: utf-8 -*-
"""
create on 2018-01-24 下午6:24

author @heyao
"""

import time
import datetime

import pymongo
from scrapy.conf import settings

from htfspider.spiders.qidian.index_male import QidianMaleIndexSpider


class QdmmIndexSpider(QidianMaleIndexSpider):
    name = 'qdmm_index'
    redis_key = 'qdmm:index'
    today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self, **kwargs):
        super(QdmmIndexSpider, self).__init__(**kwargs)

    def get_books(self):
        mongo_uri = settings.get("MONGO_URI")
        db_name = settings.get("DB_NAME")
        auth = settings.get("AUTH")
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        if auth:
            db.authenticate(**auth)
        books = set(i['book_id'] for i in db['book_index'].find({'source_id': 21}, {'book_id': 1}))
        self.books = books
