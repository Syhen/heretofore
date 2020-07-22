# -*- coding: utf-8 -*-
"""
create on 2018-02-11 下午1:53

author @heyao
"""

import time

from heretofore.main_func import get_cpu_momery_info, distribute_info, start_spider
from heretofore.spider_settings import host_list


def schedule_spider(spider_dict, mongo_db, redis_server):
    dt = time.strftime('%Y-%m-%d')

    data = {}
    for host in host_list:
        max_spider_num = get_cpu_momery_info(host, per_cpu=10, per_memory=200)
        data[host] = max_spider_num
    spider_data, dis_dict = distribute_info(data, spider_dict, mongo_db)
    for spider, host in dis_dict:
        workers = dis_dict[(spider, host)]
        total_items = len(spider_data[spider])
        print 'schdule', spider, 'on', host, 'for', workers, 'workers with', total_items, 'item'
        start_spider(redis_server, mongo_db, spider, dt, spider_data[spider], host, workers)
