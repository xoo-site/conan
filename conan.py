# coding=utf-8
"""
__purpose__ = Entry of script project
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/3 17:24]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""
import sys
import time
import json
from typing import List

from xlwt import Workbook

from core.settings import *
from core.model import meta_data
from core.collector import (BaseCollector, ProInfoCollector, NodeCollector, HardwareCollector, SoftwareCollector,
                            DiskOutputCollector, collect_and_serialize)
from utils.color import console
from utils.util import show_conf


def init():
    console(LOGO, "green")
    input("请按回车键继续...")
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    show_conf()
    check = input("确认使用以上配置进行采集吗?[Y/n]: ")
    if check.upper() != "Y":
        console("System exit bye bye.", "green")
        sys.exit(0)
    console("Start init database...")
    meta_data.create_all()


def dispatch() -> List[BaseCollector]:
    if not os.path.exists("/usr/local/sendoh/conf/node_type.csv"):
        # QPLus 类型
        return [
            ProInfoCollector(),
            NodeCollector(),
            HardwareCollector(),
            SoftwareCollector(),
            DiskOutputCollector(),
        ]
    c = BaseCollector()
    cluster_conf = c.exe(COMMANDS.get("qdatamgr_conf_show_s"))
    if not cluster_conf:
        console("[error] Read cluster conf failed, see log file for detail.")
        sys.exit(1)
    cluster_conf = json.loads(cluster_conf)
    collectors = []
    # ProInfo采集只需其中一个节点
    for node in cluster_conf:
        collectors.extend([ProInfoCollector(node["ip"], node["type"])])
        break
    for node in cluster_conf:
        console(f"Dispatch [{node['ip']}] collect tasks...")
        collectors.extend([
            NodeCollector(node["ip"], node["type"]),
            HardwareCollector(node["ip"], node["type"]),
            SoftwareCollector(node["ip"], node["type"]),
            DiskOutputCollector(node["ip"], node["type"]),
        ])
    return collectors


if __name__ == '__main__':
    init()
    collectors = dispatch()
    book = Workbook()
    console("Start collect info...")
    collect_and_serialize(book, collectors)
    book_name = BOOK.format(
        time=time.strftime("%Y%m%d%H%M%S"),
        system=CONF.get("system"),
    )
    console(f"Book [{book_name}] made succeed!", "green")
    book.save(book_name)
