# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/5 15:08]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

from core.model import *
from core.settings import DATABASE

if __name__ == '__main__':
    print(DATABASE)
    meta_data.create_all(checkfirst=True)
    print(NodeSheet.cpu_model.__doc__)
    with get_session() as session:
        all = session.query(NodeSheet).all()
        print(all)
        session.add(NodeSheet())
        print(session.query(NodeSheet).all())
