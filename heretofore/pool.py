# -*- coding: utf-8 -*-
"""
create on 2018-02-11 下午1:42

author @heyao
"""

import redis
import pymongo

from heretofore.spider_settings import mongo_uri, redis_uri, mongo_auth

con = pymongo.MongoClient(mongo_uri)
redis_connection_pool = redis.ConnectionPool.from_url(redis_uri)
db = con['htf_spider']
if mongo_auth:
    db.authenticate(**mongo_auth)
