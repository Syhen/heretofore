# -*- coding: utf-8 -*-
"""
create on 2018-03-07 上午10:16

author @heyao
"""

import re
import time
import datetime
import cPickle as pickle

import pymongo
from scrapy import Request
from scrapy.conf import settings
from scrapy_redis.spiders import RedisSpider
from htfspider.items import BookListItem


class QidianMaleIndexSpider(RedisSpider):
    name = 'qidian_index_add_field'
    redis_key = 'qidian:index'
    # today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self, **kwargs):
        super(QidianMaleIndexSpider, self).__init__(**kwargs)

    def make_request_from_data(self, data):
        data = pickle.loads(data)
        url = data.pop('data_url', None)
        if url:
            req = Request(
                url,
                meta={'data': data},
                callback=self.parse,
                dont_filter=True
            )
            return req

    def parse(self, response):
        data = response.meta['data']
        item = BookListItem()
        xpath_author_id = '//a[@class="writer"]/@href'
        item['source_id'] = data['source_id']
        item['book_id'] = response.url.split('/')[-1]
        item['author_id'] = response.xpath(xpath_author_id).extract()[0].split('=')[-1]
        item['chan_id'] = re.compile(r'chanId = (\d+);').search(response.body).group()[9:-1]
        yield item
