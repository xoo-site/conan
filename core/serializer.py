# coding=utf-8
"""
__purpose__ = Serializer for data in database dump out to excel
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/5 11:15]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""
from typing import *

from xlwt import Workbook

from core.model import BaseModel, get_session, NA
from core.model import ProInfoSheet, NodeSheet, DiskOutputSheet, SoftwareSheet, HardwareSheet
from utils.color import console


class BaseSerializer(object):
    # 需要导出的表, 即model.py中定义的表
    __model__: BaseModel.__class__ = None
    # 需要导出的字段和表头, 为保证顺序此处必须显式指定所有要导出的字段
    # 支持动态扩展字段, 例如
    #     __fields__ = (("", "xx"),)
    #     如果__model__中没有xx这个字段，则可以定义一个_get_xx(item)方法动态获取, 其中item是__model__的实例
    __fields__: Tuple[Tuple[AnyStr, AnyStr]] = ((),)
    __sheet__: AnyStr = ""  # 生成的sheet名, 为空则默认为表名

    def __init__(self, book: Workbook):
        self.book = book  # 从外部传过来的工作簿
        console(f"Model {self.__model__.__class__.__name__} excel making".center(80, "="))

    def get_sheet(self):
        """
        获取当前写入的sheet
        """
        assert isinstance(self.__sheet__, str), "Not supported sheet name"
        sheet_name = self.__sheet__ or self.__model__.__tablename__
        try:
            sheet = self.book.get_sheet(sheet_name)
        except:
            sheet = self.book.add_sheet(sheet_name, cell_overwrite_ok=True)
        return sheet

    def get_queryset(self):
        """
        需要导出的数据集合，默认为__model__表中所有记录, 如果需要筛选则覆盖此方法
        """
        assert self.__model__.__class__.__name__ == BaseModel.__class__.__name__, "Expected a %s __model__, but got %s" % (
            BaseModel.__class__.__name__,
            self.__model__.__class__.__name__,
        )
        with get_session() as session:
            queryset = session.query(self.__model__).all()
            return queryset

    def write_title(self, sheet):
        """
        写入表头
        """
        row = 0
        col = 0
        for field in self.__fields__:
            value = NA
            if field[0]:
                value = field[0]
            elif hasattr(self.__model__, field[1]):
                value = getattr(self.__model__, field[1]).__doc__
            sheet.write(row, col, value)
            col += 1

    def write_data(self, sheet, queryset):
        """
        写入数据
        """
        row = 1
        for item in queryset:
            col = 0
            for field in self.__fields__:
                # 首先从实例属性获取
                func = getattr(self, "_get_%s" % field[1], None)
                if hasattr(item, field[1]):
                    value = getattr(item, field[1])
                # 其次查看serializer是否实现了_get_<字段>方法
                elif callable(func):
                    value = func(item)
                else:
                    value = NA
                sheet.write(row, col, value)
                col += 1
            row += 1
        return sheet

    def serialize(self):
        """
        导出的具体实现
        """
        sheet = self.get_sheet()
        queryset = self.get_queryset()
        self.write_title(sheet)
        self.write_data(sheet, queryset)
        return self.book


class ProInfoSerializer(BaseSerializer):
    __model__ = ProInfoSheet
    __fields__ = (
        # (表头，字段), 如果表头为空则取model定义时的doc
        ("", "sn"),
        ("", "type_"),
        ("", "version"),
        ("", "system"),
        ("", "size"),
        ("", "sow"),
        ("", "sla"),
        ("", "desc"),
    )
    __sheet__ = ProInfoSheet.__tablename__


class NodeSerializer(BaseSerializer):
    __model__ = NodeSheet
    __fields__ = (
        ("", "sn"),
        ("", "type_"),
        ("", "is_woqu_maintenance"),
        ("", "hostname"),
        ("", "product_sn"),
        ("", "order"),
        ("", "brand"),
        ("", "model"),
        ("", "raid"),
        ("", "ib"),
        ("", "flash"),
        ("", "cpu_model"),
        ("", "cpu_num"),
        ("", "memory_size"),
        ("", "memory_num"),
    )
    __sheet__ = "节点"


class HardwareSerializer(BaseSerializer):
    __model__ = HardwareSheet
    __fields__ = (
        ("", "type_"),
        ("", "is_woqu_maintenance"),
        ("", "model"),
        ("", "brand"),
        ("", "sn"),
        ("", "order"),
        ("", "firmware"),
        ("", "is_produced_by_server"),
        ("", "node_sn"),
    )
    __sheet__ = "硬件"


class SoftwareSerializer(BaseSerializer):
    __model__ = SoftwareSheet
    __fields__ = (
        ("", "sn"),
        ("", "node_sn"),
        ("", "order"),
    )
    __sheet__ = "软件"


class DiskOutputSerializer(BaseSerializer):
    __model__ = DiskOutputSheet
    __fields__ = (
        ("", "ip"),
        ("", "output"),
    )
    __sheet__ = "硬盘输出详情"
