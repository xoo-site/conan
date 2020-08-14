# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/5 19:32]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""
import logging

from core.settings import *
from core.model import NodeSheet, get_session, ProInfoSheet

logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL, format=LOG_FMT, datefmt=DATE_FMT)

if __name__ == '__main__':
    with get_session() as s:
        node = s.query(NodeSheet).first()
        node.show()
