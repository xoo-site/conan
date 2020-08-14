# coding=utf-8
"""
__purpose__ = ssh, sftp connect for host in cluster
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/7/24 15:04]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""
import os
import re
from contextlib import contextmanager

import paramiko

from utils.color import console, logger


def get_ssh_port():
    """
    获取ssh端口
    # todo: 优化逻辑
    """
    default = 22
    cmd = "cat /etc/ssh/sshd_config |grep 'Port'"
    result = os.popen(cmd).read()
    logger.info(result)
    lines = [line.strip() for line in result.splitlines()]
    for line in lines:
        if line.startswith('Port'):
            items = [item for item in line.split(' ') if item]
            try:
                return int(items[1])
            except Exception as e:
                logger.error(e)
    return default


@contextmanager
def open_ssh(hostname, user, password, port=22, timeout=20):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, user, password, timeout=timeout)
    yield client
    client.close()


def make_client(ip, port, username, password):
    """
    获取ssh和ftp连接
    """
    try:
        transport = paramiko.Transport((ip, port))
        transport.connect(username=username, password=password)
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sftp = paramiko.SFTPClient.from_transport(transport)
    except Exception as e:
        logger.error("%s创建连接失败: %s" % (ip, e))
        return None, None, None
    logger.info("%s创建连接成功" % ip)
    setattr(ssh, "ip", ip)
    return ssh, sftp, transport


def get_os_version(ssh=None):
    """
    获取操作系统的主要版本
    :param ssh:
    :return:
    """
    pattern = re.compile(r"release[\s\t]*(\d\.?\d)")
    cmd = "cat /etc/redhat-release"
    if ssh:
        result = ssh.exec_command(cmd).read()
    else:
        f = os.popen(cmd)
        result = f.read()
        f.close()
    match = pattern.search(result)
    if match:
        version = match.group(1)
        return version.split(".")[0]
    return "7"


def auto_ssh(hostname, user, password=None, port=22, timeout=20, key_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, user, password=password, timeout=timeout, key_filename=key_file)
    return client
