# -*- coding: utf-8 -*-
"""
create on 2018-02-27 下午5:04

author @heyao
"""

from datetime import datetime

import redis

from hm_collections.queue.redis_queue import RedisSetQueue

from heretofore.master_func import generate_id_coll, generate_data
from heretofore.pool import redis_connection_pool, db

r = redis.StrictRedis(connection_pool=redis_connection_pool)


def add_data(data, spider_name):
    queue = RedisSetQueue(r, spider_name.replace('_', ':'))
    for i in data:
        queue.push(i)


def remove_queue_data(spider_name):
    queue = RedisSetQueue(r, spider_name.replace('_', ':'))
    queue.flush()


def remove_mongo_data(spider_name):
    today = datetime.now()
    today = datetime(today.year, today.month, today.day)
    source_id, data_coll = generate_id_coll(spider_name)
    data = list(db[data_coll].find({'source_id': source_id}))
    # 备份数据
    db[data_coll + '_copy'].delete_many({'source_id': source_id})
    if data:
        db[data_coll + '_copy'].insert_many(data)
    if 'detail' in data_coll:
        data = list(db[data_coll + '_history'].find({'source_id': source_id, 'history_created_at': today}))
        if data:
            db[data_coll + '_history_copy'].insert_many(data)
    # 删除数据
    if 'detail' in data_coll:
        db[data_coll].delete_many({'source_id': source_id})
        db[data_coll + '_history'].delete_many({'source_id': source_id, 'history_created_at': today})


def start_ceshi(spider_name, limit=5):
    data = generate_data(spider_name, db, limit=limit)
    remove_queue_data(spider_name)
    remove_mongo_data(spider_name)
    add_data(data, spider_name)
