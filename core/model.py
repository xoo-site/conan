# coding=utf-8
"""
__purpose__ = model class for each sheet
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/3 17:24]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

import logging
from contextlib import contextmanager
from collections import Iterable

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Enum, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.orm.attributes import InstrumentedAttribute

from core.settings import DATABASE
from utils.prettytable import PrettyTable

logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///{0}".format(DATABASE), encoding='utf8', echo=False)
meta_data = MetaData(bind=engine)


@contextmanager
def get_session():
    Session = sessionmaker(bind=engine, autocommit=True, autoflush=True, expire_on_commit=False)
    session = Session()
    yield session
    session.close()


def open_session():
    Session = sessionmaker(bind=engine, autocommit=True, autoflush=True, expire_on_commit=False)
    session = Session()
    return session


class Base(object):
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)

    def show(self, exclude=("id",)):
        """
        终端表格显示
        """
        assert isinstance(exclude, Iterable), "Expected a %s, but got %s." % (
            Iterable.__name__,
            exclude.__class__.__name__,
        )
        table = PrettyTable(["指标名称", "取值"])
        for attr_name in self.__class__.__dict__:
            cls_attr = getattr(self.__class__, attr_name)
            condition = ((isinstance(cls_attr, InstrumentedAttribute) and (attr_name not in exclude)) if exclude
                         else isinstance(cls_attr, InstrumentedAttribute))
            if condition:
                attr = getattr(self, attr_name)
                table.add_row([cls_attr.__doc__, attr])
        print(table)
        logger.info("\n%s" % table)


BaseModel = declarative_base(bind=engine, name='BaseModel', metadata=meta_data, cls=Base)

# Enum types used in project
NA = "N/A"
Y = "是"
N = "否"
Y_N = Enum(Y, N)
STANDARD = "QDataStandard"
LITE = "QDataLite"
QPLUS = "QPlus"
PRODUCT_TYPES = Enum(STANDARD, LITE, QPLUS, NA)

COMPUTE = "compute"
STORAGE = "storage"
SANFREE = "sanfree"
NODE_TYPES = Enum(COMPUTE, STORAGE, SANFREE, QPLUS, NA)


class ProInfoSheet(BaseModel):
    __tablename__ = "proinfo"
    sn = Column(String(length=128), nullable=True, default=NA, doc="产品序列号")
    type_ = Column(PRODUCT_TYPES, nullable=True, default=NA, doc="产品类型")
    version = Column(String(length=32), nullable=True, default=NA, doc="产品版本")
    system = Column(String(length=32), nullable=True, default=NA, doc="业务系统")
    size = Column(String(length=16), nullable=True, default=NA, doc="产品规模")
    sow = Column(String(length=16), nullable=True, default=NA, doc="sow")
    sla = Column(String(length=16), nullable=True, default=NA, doc="sla")
    desc = Column(String(length=64), nullable=True, default=NA, doc="产品说明")


class NodeSheet(BaseModel):
    __tablename__ = "node"
    sn = Column(String(length=64), nullable=True, default=NA, doc="节点序列号")
    type_ = Column(NODE_TYPES, nullable=True, default=NA, doc="节点类型")
    is_woqu_maintenance = Column(Y_N, nullable=True, default=N, doc="是否属于沃趣维保")
    hostname = Column(String(length=16), nullable=True, default=NA, doc="主机名称")
    product_sn = Column(String(length=32), nullable=True, default=NA, doc="产品序列号")
    order = Column(String(length=32), nullable=True, default=NA, doc="订单号")
    brand = Column(String(length=64), nullable=True, default=NA, doc="节点品牌")
    model = Column(String(length=32), nullable=True, default=NA, doc="节点型号")
    raid = Column(String(length=32), nullable=True, default=NA, doc="RAID卡驱动")
    ib = Column(String(length=32), nullable=True, default=NA, doc="IB卡驱动")
    flash = Column(String(length=32), nullable=True, default=NA, doc="FLASH卡驱动(类型+驱动号)")
    cpu_model = Column(String(length=128), nullable=True, default=NA, doc="CPU型号")
    cpu_num = Column(String(length=4), nullable=True, default=NA, doc="CPU个数")
    memory_size = Column(String(length=6), nullable=True, default=NA, doc="内存大小(GB)")
    memory_num = Column(String(length=4), nullable=True, default=NA, doc="内存个数")


class HardwareSheet(BaseModel):
    __tablename__ = "hardware"
    type_ = Column(String(length=7), nullable=True, default=NA, doc="配件类型")
    is_woqu_maintenance = Column(Y_N, default=N, nullable=True, doc="是否属沃趣维保")
    model = Column(String(length=64), nullable=True, default=NA, doc="型号")
    brand = Column(String(length=32), nullable=True, default=NA, doc="配件品牌")
    sn = Column(String(length=32), nullable=True, default=NA, doc="配件序列号")
    order = Column(String(length=32), nullable=True, default=NA, doc="订单号")
    firmware = Column(String(length=32), nullable=True, default=NA, doc="固件版本")
    is_produced_by_server = Column(Y_N, nullable=True, default=N, doc="是否随服务器采购")
    node_sn = Column(String(length=32), nullable=True, default=NA, doc="节点序列号")


class SoftwareSheet(BaseModel):
    __tablename__ = "software"
    sn = Column(String(length=32), nullable=True, default=NA, doc="软件序列号")
    node_sn = Column(String(length=32), nullable=True, default=NA, doc="节点序列号")
    order = Column(String(length=32), nullable=True, default=NA, doc="订单号")


class DiskOutputSheet(BaseModel):
    __tablename__ = "disk_output"
    ip = Column(String(length=64), nullable=True, default=NA, doc="IP")
    output = Column(TEXT, nullable=True, default=NA, doc="硬盘输出")
