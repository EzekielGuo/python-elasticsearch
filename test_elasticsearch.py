# encoding: utf-8
'''
@author: guozhijie
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: guo.zhijie@21vianet.com
@software: pycharm
@file: elasticsearch.py
@time: 2018/9/25 15:03
@desc:脚本原理：查询本月所有该端口down的时间戳，放在一个列表中，根据每个时间戳继续轮询该端口up的时间戳，取uptime>=downtime的部分，放在一个列表中排序，取第0个，计算差值，单位为s。可能某设备某端口一个月内也不会有一条日志出现在elk的情况，此时应判定端口可用率为 100% 或 0% 。
'''

from elasticsearch import Elasticsearch
import time
import datetime
import os


def elastic(ip,port,index):
    ## 创建连接
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 10000}])
    ## 闪断次数
    flash = 0
    ## 端口总中断时间
    duration_all = 0
    ## 输出的信息
    info = {}
    detail = []
    ## 错误时输出的信息
    info_Exception = []
    ## 端口down的时间戳列表
    list_downtime = []
    ## 端口断开总时长
    try:
        ## 端口down,up查询语句
        question_down = 'host:"{}" AND message:"{}" AND message:"down"'.format(ip,port)
        question_up = 'host:"{}" AND message:"{}" AND message:"up"'.format(ip,port)
        # print(question_down)
        res_down = es.search(index=index,q=question_down,size=10000)
        # print(res_down)

        for hit_down in res_down['hits']['hits']:
            downtime_str = hit_down['_source']['@timestamp']
            downtime_float = downtime_str[:-5]
            downtime_struct = datetime.datetime.strptime(downtime_float, '%Y-%m-%dT%H:%M:%S')
            downtime_stamp = time.mktime(downtime_struct.timetuple())
            list_downtime.append(downtime_stamp)
            list_downtime.sort()
            # print('list_downtime:{}'.format(list_downtime))

        ## 列表去重
        list_downtime = list(set(list_downtime))
        # print('list_downtime:{}'.format(list_downtime))

        for downtime in list_downtime:
            # print('downtime:{}'.format(downtime))
            list_uptime = []
            res_up = es.search(index=index, q=question_up, size=10000)
            # print('res_up：{}'.format(res_up))
            for hit_up in res_up['hits']['hits']:
                uptime_str = hit_up['_source']['@timestamp']
                uptime_float = uptime_str[:-5]
                uptime_struct = datetime.datetime.strptime(uptime_float, '%Y-%m-%dT%H:%M:%S')
                uptime_stamp = time.mktime(uptime_struct.timetuple())
                if uptime_stamp >= downtime:
                    list_uptime.append(uptime_stamp)
            list_uptime.sort()
            uptime = list_uptime[0]
            # print('uptime:{}'.format(uptime))
            ## 断开时长
            duration = uptime - downtime
            duration_all += duration
            # print('duration:{}'.format(duration))
            # print('duration_all:{}'.format(duration_all))
            ## 端口闪断
            if duration == 0:
                flash += 1

            ## 将时间戳转化为时间
            downtime_local = time.localtime(downtime)
            # print('downtime_local:{}'.format(downtime_local))
            downtime_view = time.strftime("%Y-%m-%d %H:%M:%S", downtime_local)
            # print('downtime_view:{}'.format(downtime_view))

            uptime_local = time.localtime(uptime)
            # print('uptime_local:{}'.format(uptime_local))
            uptime_view = time.strftime("%Y-%m-%d %H:%M:%S", uptime_local)
            # print('uptime_view:{}'.format(uptime_view))

            ## 追加到info
            info_dic = {}
            info_dic['downtime'] = downtime_view
            info_dic['uptime'] = uptime_view
            info_dic['duration'] = duration
            # print('info_dic:{}'.format(info_dic))
            detail.append(info_dic)
        ## 可用率
        ratio = (1 - (duration_all / (30 * 24 * 60 * 60))) * 100
        ratio = round(ratio,2)
        # print('ratio:{}'.format(ratio))
        # print('detail:{}'.format(detail))
        # print('flash:{}'.format(flash))
        info['detail'] = detail
        info['flash'] = flash
        info['ratio'] = ratio
        print(info)

        return info

    except Exception:
        exception = 'Exception'
        return exception

# 拼出当月索引
localtime = time.localtime(time.time())
year_str = str(localtime[0])
month = localtime[1]
month_str = 0
if month < 10:
    month_str = "0" + str(month)
es_index = 'ordinary-' + year_str + '.' + month_str + '*'
# print(es_index)

# 参数
ip = ''
port = ''
index = es_index
elastic(ip,port,index)

