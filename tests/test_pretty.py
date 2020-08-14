# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/3 18:03]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

from utils import prettytable as pt
from utils.util import show_conf


def test_tb():
    table = pt.PrettyTable(["配件类型", "是否属于沃趣维保", "型号", "配件品牌", "配件序列号", "订单号", "固件版本"])
    for i in range(20):
        table.add_row([
            "HDD",
            True,
            "Intel S4510 960GB",
            "Intel",
            "ST3312345",
            "WQ-20200803001",
            "ST133",
        ])
    print(table)


if __name__ == '__main__':
    show_conf()
