# -*- coding: utf-8 -*-
"""
create on 2018-02-27 下午5:34

author @heyao
"""

from argparse import ArgumentParser

from heretofore.run.ceshi.utils import start_ceshi


parser = ArgumentParser()
parser.add_argument('spider')
parser.add_argument('limit')

args = parser.parse_args()
spider = args.spider
limit = int(args.limit)

start_ceshi(spider, limit)
