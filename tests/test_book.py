# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/5 16:04]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

from xlwt import Workbook

from core.serializer import NodeSerializer, BaseSerializer


class ErrorSerializer(BaseSerializer):
    __model__ = ImportError
    __fields__ = ()
    __sheet__ = "error"


if __name__ == '__main__':
    book = Workbook()
    s = NodeSerializer(book)
    s.serialize()
    # es = ErrorSerializer(book)
    # es.serialize()
    book.save("test.xls")
