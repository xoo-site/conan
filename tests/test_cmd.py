# coding=utf-8
"""
__purpose__ = ...
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/7 18:18]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

from utils.ssh import open_ssh, auto_ssh
from core.collector import BaseCollector
from core.settings import COMMANDS
from utils.pymegacli import MegaCLIBase

if __name__ == '__main__':
    # c = BaseCollector()
    # c.exe("ls -al")
    # with open_ssh("10.10.100.12", "root", "cljslrl0620") as ssh:
    #     d = BaseCollector(ssh)
    #     d.exe(COMMANDS.get("qdatamgr_conf_show_s"))
    # ssh = auto_ssh("10.10.100.216", "root", key_file="/root/.ssh/id_rsa")
    # ssh.exec_command("hostname")
    m = MegaCLIBase("/usr/sbin/MegaCli")
    m.run_command('-pdlist -aall')
    for c in m.controllers:
        # 控制器  -a0  可以使用

        print(c.controller_number)
        for d in c.PDs:
            # 编号 PhysDrv [32:0]
            print(d.identifier)
