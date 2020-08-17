# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/6 14:49]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

from utils.prettytable import PrettyTable
from utils.color import console, logger
from core.settings import CONF, COMMANDS


def show_conf():
    """
    展示当前配置
    """
    # 基本配置信息
    base_table = PrettyTable(["配置项", "当前配置值"])
    base_table.add_row(["是否开启调试模式", CONF.get("debug", True)])
    base_table.add_row(["ssh端口", int(CONF.get("ssh_port", 22))])
    base_table.add_row(["订单号", CONF.get("order", "WQXSDD-2020-000")])
    base_table.add_row(["是否属于沃趣维保", CONF.get("is_woqu_maintenance", False)])
    base_table.add_row(["客户业务系统", CONF.get("system", "xx客户xx系统")])
    base_table.add_row(["是否随服务器采购", CONF.get("is_produced_by_server", False)])
    base_table.add_row(["是否采集ib交换机", CONF.get("is_collect_switch", False)])
    console("基本配置信息", "white")
    console(base_table, "blue")
    # 交换机配置信息
    if CONF.get("is_collect_switch", False):
        switch_table = PrettyTable(["ip", "port", "username", "password"])
        switches = CONF.get("switch", [])
        [switch_table.add_row([s["ip"], s["port"], s["username"], s["password"]]) for s in switches]
        console("交换机配置信息", "white")
        console(switch_table, "blue")
