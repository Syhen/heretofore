# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

from flask import jsonify, request

from app import basic_auth
from app.exceptions import ApiExceptions, UNAUTHORIZED, INTERNAL_SERVER_ERROR
from . import api
from .. import task_redis
from heretofore.runner.scheduler import SpiderTaskScheduler
from heretofore.sh import MonitProcess

scheduler = SpiderTaskScheduler(spider_path='/Users/heyao/heretofore/heretofore/htfspider', spider_pid_file_path='/Users/heyao/heretofore/heretofore/var')
monitor_process = MonitProcess()


@basic_auth.error_handler
def unauthorized():
    raise ApiExceptions(code=UNAUTHORIZED, msg='Unauthorized')


@api.route('/')
# @basic_auth.login_required
def index():
    return jsonify(code=200, msg="I'm alive", data=None)


@api.route('/schedul/<spider_name>')
# @basic_auth.login_required
def schedul(spider_name):
    workers = request.args.get('workers', 1)
    try:
        workers = int(workers)
    except ValueError as e:
        raise ApiExceptions(INTERNAL_SERVER_ERROR, msg=e.message)
    scheduler.schedule(spider_name, workers)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/pause/<spider_name>')
# @basic_auth.login_required
def pause(spider_name):
    scheduler.pause(spider_name)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/resume/<spider_name>')
# @basic_auth.login_required
def resume(spider_name):
    scheduler.resume(spider_name)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/stop/<spider_name>')
# @basic_auth.login_required
def stop(spider_name):
    force = request.args.get('force', 0)
    try:
        force = int(force)
    except ValueError as e:
        raise ApiExceptions(INTERNAL_SERVER_ERROR, msg=e.message)
    scheduler.stop(spider_name, task_redis, force)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/finished/<spider_name>')
# @basic_auth.login_required
def is_finished(spider_name):
    b = scheduler.is_finished(spider_name, task_redis)
    return jsonify(code=200, msg='SUCCESS', data={'finished': b})


@api.route('/memory')
# @basic_auth.login_required
def memory():
    """内容使用情况
    :return: 
    """
    memory_info = monitor_process.memory_state()
    keys = ['total', 'free', 'available', 'used', 'active', 'inactive', 'wired']
    percent = memory_info.percent
    memory_info = {k: round(getattr(memory_info, k) * 1. / 1024 / 1024, 2) for k in keys}
    memory_info['percent'] = percent
    return jsonify(code=200, msg='SUCCESS', data=dict(**memory_info))


@api.route('/cpu')
# @basic_auth.login_required
def cpu():
    cpu_info = monitor_process.cup_state(3)
    return jsonify(code=200, msg='SUCCESS', data=dict(cpu_percent=cpu_info))
