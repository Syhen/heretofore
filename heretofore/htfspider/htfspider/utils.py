# -*- coding: utf-8 -*-
"""
create on 2018-02-04 下午2:33

author @heyao
"""

import os
import requests

usernm = os.environ.get("SPIDER_USERNAME")
passwd = os.environ.get("SPIDER_PASSWORD")


def authorized_requests(method, url, username='', password='', **kwargs):
    username = username or usernm
    password = password or passwd
    headers = kwargs.pop('headers', {})
    headers.update({'User-Agent': 'htf-subordinate'})
    response = requests.request(method, url, headers=headers, auth=(username, password), **kwargs)
    content = response.content
    response.close()
    return content
