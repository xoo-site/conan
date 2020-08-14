# coding=utf-8
"""
__purpose__ = global settings for project
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/3 17:24]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

import os
import logging

import yaml

# 当前软件版本
VERSION = "3.3.0-dev"

# 项目根目录
BASE_DIR = os.getcwd()

# 配置文件路径
CONF_PATH = os.path.join(BASE_DIR, "config.yml")

# 日志保存路径
LOG_PATH = os.path.join(BASE_DIR, 'conan.log')

# 读取config.yml用户自定义配置
CONF = yaml.safe_load(open(CONF_PATH))

# 运行模式: debug开启则会显示命令执行详细信息
DEBUG = CONF.get("debug", True)

# 日志级别
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# 日志保存格式
LOG_FMT = '[%(name)s %(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s'

# 时间序列化格式
DATE_FMT = "%Y-%m-%d %H:%M:%S"

# 数据库
DATABASE = os.path.join(BASE_DIR, "db.sqlite3")

# 脚本运行时的logo
LOGO = r"""
Try to collect some information and make it into a excel documentation.
   ___ ___  _ __   __ _ _ __
  / __/ _ \| '_ \ / _` | '_ \       Author: JeeysheLu
 | (_| (_) | | | | (_| | | | |      Version: %s
  \___\___/|_| |_|\__,_|_| |_|      Good Luck to You!

""" % VERSION

# 采集过程需要使用的命令, 放在config.yml中, 允许临时修改
COMMANDS = CONF.get("commands", {})

# 工作簿名称模板
BOOK = os.path.join(BASE_DIR, "{time}-WOQUProInfo-{system}.xls")
