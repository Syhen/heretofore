# -*- coding: utf-8 -*-
"""
create on 2018-02-11 下午2:17

author @heyao
"""

import redis

from heretofore.run.utils import schedule_spider
from heretofore.pool import db, redis_connection_pool

r = redis.StrictRedis(connection_pool=redis_connection_pool)
schedule_spider({'chuangshi_index': 1, 'yunqi_index': 1}, db, r)
