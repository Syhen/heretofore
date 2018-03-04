# -*- coding: utf-8 -*-
"""
create on 2018-03-04 下午3:13

author @heyao
"""

import redis

from hm_collections.queue.redis_queue import RedisSetQueue

from heretofore.pool import redis_connection_pool

r = redis.StrictRedis(connection_pool=redis_connection_pool)

spider_names = ['qidian_index', 'xxsy_index', 'jjwxc_index', 'chuangshi_index', 'yunqi_index', 'qdmm_index']
url_formats = {
    'qidian': {
        'url': 'https://www.qidian.com/all?orderId=2&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page={page}',
        'total_page': 100
    },
    'qdmm': {
        'url': 'https://www.qidian.com/mm/all?orderId=2&style=1&pageSize=20&siteid=0&pubflag=0&hiddenField=0&page={page}',
        'total_page': 30
    },
    'jjwxc': {
        'url': 'http://www.jjwxc.net/bookbase.php?fw0=0&fbsj=0&ycx0=0&xx0=0&mainview0=0&sd0=0&lx0=0&fg0=0&sortType=4&isfinish=0&collectiontypes=ors&searchkeywords=&page={page}',
        'total_page': 20
    },
    'chuangshi': {
        'url': 'http://chuangshi.qq.com/bk/so5/p/{page}.html',
        'total_page': 70
    },
    'xxsy': {
        'url': 'http://www.xxsy.net/search?s_wd=&vip=1&sort=4&pn={page}',
        'total_page': 30
    },
    'yunqi': {
        'url': 'http://yunqi.qq.com/bk/so12/n30p{page}',
        'total_page': 50
    }
}


def get_source_id(spider_type):
    return dict(
        qidian=1,
        qdmm=21,
        xxsy=6,
        jjwxc=7,
        chuangshi=8,
        yunqi=11
    )[spider_type]


for spider_name in spider_names:
    spider_type = spider_name.split('_')[0]
    queue = RedisSetQueue(r, spider_name.replace('_', ':'))
    data = url_formats[spider_type]
    url_format = data['url']
    pages = data['total_page']
    source_id = get_source_id(spider_type)
    for page in range(1, pages + 1):
        url = url_format.format(page=page)
        d = {
            'data_url': url,
            'source_id': source_id
        }
        queue.push(d)
