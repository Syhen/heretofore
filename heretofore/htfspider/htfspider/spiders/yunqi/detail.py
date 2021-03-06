# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/22 14:48
    @subject: 云起小说网 http://yunqi.qq.com
"""
import re
import json
import time
from collections import Counter
from datetime import datetime
import cPickle as pickle


from scrapy import Request, Selector
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookDetailItem


class YunqiDetailSpider(RedisSpider):
    name = 'yunqi_detail'
    redis_key = 'yunqi:detail'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

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
        item = BookDetailItem()
        item.update(response.meta['data'])
        item['source_id'] = 11
        item['book_id'] = response.url.split('/')[-1].split('.')[0]
        if '小说不存在' in response.body:
            item['status'] = 0
            yield item
            return
        item['book_status'] = 1
        item['total_word'] = int(response.xpath(u'string(//td[contains(.,"总字数")])').extract()[0].split(u'：')[1].strip())
        item['total_click'] = int(
            response.xpath(u'string(//td[contains(.,"总点击")])').extract()[0].split(u'：')[1].strip())
        item['total_recommend'] = int(
            response.xpath(u'string(//td[contains(.,"总人气")])').extract()[0].split(u'：')[1].strip())
        item['book_status'] = response.xpath('//div[@id="novelInfo"]//span[@class="red2"]/text()').extract()[0]
        book_updated_at = response.xpath('//div[@class="chaptername"]/text()').extract()[0]
        item['book_updated_at'] = datetime.strptime(re.findall(r"\d{4}-\d+-\d+", book_updated_at)[0], '%Y-%m-%d')
        headers = {'Referer': 'http://yunqi.qq.com/bk/ds/{}.html'.format(item['book_id'])}
        yield Request(
            url='http://yunqi.qq.com/novelcomment/index.html?bid={}'.format(item['book_id']),
            headers=headers,
            meta={'item': item},
            callback=self.parse_total_comment,
            dont_filter=True
        )

    def parse_total_comment(self, response):
        """
        获取该书评论数
        :param response:
        :return:
        """
        item = response.meta['item']
        comment_json = json.loads(response.body)
        item['total_comment'] = int(comment_json['data']['commentNum'])
        yield Request(
            url='http://yunqi.qq.com/novel/interactCenter.html?bid={}&tab=0'.format(item['book_id']),
            meta={'item': item},
            callback=self.parse_total,
            dont_filter=True
        )

    def parse_total(self, response):
        item = response.meta['item']
        total_json = json.loads(response.body)
        total = total_json['content']
        sel = Selector(text=total)
        try:
            item['total_ticket'] = int(
                sel.xpath('//*[@id="swishnev001"]/div[1]/ul/li[1]/b[2]/span/text()').extract()[0])
            ticket_rank = sel.xpath('//*[@id="swishnev001"]/div[1]/ul/li[1]/b[2]/text()[2]').extract()[0]
            item['ticket_rank'] = int(re.findall(r'(\d+)', ticket_rank)[0])
        except IndexError:
            item['total_ticket'] = -1
            item['ticket_rank'] = -1
        item['reward'] = int(sel.xpath('//a[@class="tab02"]/span/text()').extract()[0])
        item['updated_at'] = self.today
        score_url = 'http://android.reader.qq.com/v6_3_5/nativepage/book/detail?bid={}'.format(item['book_id'])
        yield Request(
            url=score_url,
            meta={'item': item},
            callback=self.parse_score,
            dont_filter=True
        )

    def parse_score(self, response):
        """
        获取该书评分、评分人数
        :param response:
        :return:
        """
        item = response.meta['item']
        score_json = json.loads(response.body)
        if '暂无评分' in response.body or score_json['code'] != 0:
            item['total_score'] = -1.0
            item['total_scored_user'] = -1
        elif 'scoretext' not in score_json['introinfo']['scoreInfo'].keys():
            item['total_score'] = -1.0
            item['total_scored_user'] = -1
        else:
            item['total_score'] = float(score_json['introinfo']['scoreInfo']['scoretext'])
            total_scored_user = score_json['introinfo']['scoreInfo']['intro']
            if '小编评分' in total_scored_user:
                item['total_scored_user'] = -1
            else:
                item['total_scored_user'] = self.str2num(total_scored_user[1: -3])
        fans_page = 1
        item['fans'] = []
        fans_url = 'http://yunqi.qq.com/novel/getNovelfansajax.html?bid={0}&page={1}'.format(
            item['book_id'], fans_page)
        yield Request(
            url=fans_url,
            meta={'item': item, 'fans_page': fans_page, 'fans_level': []},
            callback=self.parse_fans,
            dont_filter=True
        )

    def parse_fans(self, response):
        item = response.meta['item']
        fans_page = response.meta['fans_page']
        fans_level = response.meta['fans_level']
        if 'liri' not in response.body:
            yield item
        else:
            fans_html = json.loads(response.body)['data']['html']
            sel = Selector(text=fans_html)
            fans_level.extend(sel.xpath('//b[@class="liri"]/text()').extract())
            counter = Counter(fans_level)
            item['fans'] = [{'name': k, 'value': counter[k]} for k in counter]
            fans_page += 1
            fans_url = 'http://yunqi.qq.com/novel/getNovelfansajax.html?bid={0}&page={1}'.format(
                item['book_id'], fans_page)
            yield Request(
                url=fans_url,
                meta={'item': item, 'fans_page': fans_page, 'fans_level': fans_level},
                callback=self.parse_fans,
                dont_filter=True
            )

    def str2num(self, string):
        """
        评论人数万和亿为单位
        :param string:
        :return:
        """
        if '万' in string:
            return int(float(string[:-1]) * 10000)
        elif '亿' in string:
            return int(float(string[:-1]) * 100000000)
        else:
            return int(string)
