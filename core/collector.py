# coding=utf-8
"""
__purpose__ = Collector for each hardware type
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/7 11:56]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""
import os
import re
import json
from typing import List
import gc

from xlwt import Workbook
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.inspection import inspect

from core.model import BaseModel, ProInfoSheet, NodeSheet, SoftwareSheet, HardwareSheet, DiskOutputSheet
from core.model import QPLUS, open_session, STORAGE, COMPUTE, SANFREE, STANDARD, LITE, NA, yes_or_no
from core.serializer import (BaseSerializer, ProInfoSerializer, NodeSerializer, SoftwareSerializer, HardwareSerializer,
                             DiskOutputSerializer)
from utils.color import console, logger
from core.settings import DEBUG, CONF, COMMANDS
from utils.ssh import auto_ssh, get_ssh_port
from utils.pymegacli import MegaCLIBase


class BaseCollector(object):
    # 需要保存到的model类
    model_class: BaseModel.__class__ = None
    # 需要序列化的类
    serializer_class: BaseSerializer.__class__ = None

    def __init__(self, ip=None, node_type=None, hardware_id=None, data=None):
        self.ip = ip
        if not self.ip:
            self.node_type = QPLUS
        else:
            self.node_type = node_type
        self.hardware_id = hardware_id
        self.session = open_session()
        port = int(CONF.get("ssh_port", 22)) or get_ssh_port()
        self.ssh = auto_ssh(
            hostname=ip,
            user="root",
            port=port,
            timeout=20,
            key_file="/root/.ssh/id_rsa"
        )
        # 用于保存一些共用信息的字典
        self.data = data or {}
        if self.node_type in [QPLUS]:
            self.megacli_bin = COMMANDS.get("qplus_megacli_bin")
        else:
            self.megacli_bin = COMMANDS.get("qdata_megacli_bin")
        if self.ip:
            if self.hardware_id:
                console(f"Host {self.ip} {self.__class__.__name__} Hardware[{self.hardware_id}]".center(80, "="))
            else:
                console(f"Host {self.ip} {self.__class__.__name__} Collect".center(80, "="))
        else:
            console(f"Local Host {self.__class__.__name__} Collect".center(80, "="))

    def exe(self, cmd, timeout=20):
        """
        执行命令: ssh存在则在会话执行，否则在本地执行
        """
        if DEBUG:
            console(f"[cmd] {cmd}", "white")
        else:
            logger.info(f"[cmd] {cmd}")
        if self.ssh:
            try:
                _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
            except Exception as e:
                if DEBUG:
                    console(f"[error] Error occurred.", "red")
                else:
                    logger.error(e)
                return "{}"
            else:
                out = stdout.read()
                err = stderr.read()
                if isinstance(out, bytes):
                    out = out.decode()
                if DEBUG:
                    console(f"[stdout] {out}", "green")
                    console(f"[stderr] {err}", "yellow")
                else:
                    logger.info(f"[stdout] {out}")
                    logger.warn(f"[stderr] {err}")
                return out
        else:
            try:
                f = os.popen(cmd)
            except Exception as e:
                if DEBUG:
                    console(f"[error] Error occurred.", "red")
                else:
                    logger.error(e)
                return "{}"
            else:
                out = f.read()
                err = f.errors
                if isinstance(out, bytes):
                    out = out.decode()
                if DEBUG:
                    console(f"[stdout] {out}", "green")
                    console(f"[stderr] {err}", "yellow")
                else:
                    logger.info(f"[stdout] {out}")
                    logger.warn(f"[stderr] {err}")
                f.close()
                return out

    def collect(self, exclude=("id",)):
        data = {}
        # 寻找实例的get_<字段名>方法进行调用获得指标值

        # 手动实现的找到model中所有定义的 column
        # for attr_name in self.model_class.__dict__:
        #     cls_attr = getattr(self.model_class, attr_name)
        #     condition = ((isinstance(cls_attr, InstrumentedAttribute) and (attr_name not in exclude)) if exclude
        #                  else isinstance(cls_attr, InstrumentedAttribute))
        #     if condition:
        #         func = getattr(self, f"get_{attr_name}")
        #         if callable(func):
        #             data[attr_name] = func()

        # sqlalchemy 实现的寻找model中所有定义的 column
        fields = inspect(self.model_class).columns.keys()
        for filed in fields:
            if filed not in exclude:
                func = getattr(self, f"get_{filed}", None)
                if callable(func):
                    data[filed] = func()

        # 入库
        instance = self.model_class(**data)
        self.session.add(instance)
        self.session.flush()
        instance.show()
        return data

    def serialize(self, book: Workbook):
        """
        实例化序列器生成一个sheet
        """
        serializer = self.serializer_class(book)
        return serializer.serialize()

    def close(self):
        """
        结束采集
        """
        try:
            self.session.close()
            self.ssh.close()
        except Exception as e:
            if DEBUG:
                console(f"[warn] seems session or ssh close failed: {e}")
            else:
                logger.error(e)
        # 手动触发gc回收，虽然这可能并没有什么卵用
        gc.collect()


def collect_and_serialize(book: Workbook, collectors: List[BaseCollector]):
    """
    采集保存并导出为sheet
    """
    for collector in collectors:
        collector.collect()
        collector.serialize(book)
        collector.close()


def collect_only(collectors: List[BaseCollector]):
    """
    仅采集保存
    """
    for collector in collectors:
        collector.collect()
        collector.close()


class ProInfoCollector(BaseCollector):
    """
    产品信息sheet采集
    """
    model_class = ProInfoSheet
    serializer_class = ProInfoSerializer

    def get_sn(self):
        """
        获取序列号
        """
        if self.node_type in [SANFREE, COMPUTE, STORAGE]:
            cluster = json.loads(self.exe(COMMANDS.get("qdatamgr_conf_show_s")))
            for node in cluster:
                return node.get("cluster_uuid")
        if self.node_type in [QPLUS]:
            info = json.loads(self.exe(COMMANDS.get("zstack_cli_license")))
            return info.get("inventory", {}).get("serialNumber")

    def get_type_(self):
        """
        产品类型
        """
        map = {
            SANFREE: LITE,
            COMPUTE: STANDARD,
            STORAGE: STANDARD,
            QPLUS: QPLUS,
        }
        return map.get(self.node_type)

    def get_version(self):
        """
        获取产品版本
        """
        if self.node_type in [SANFREE, COMPUTE, STORAGE]:
            return self.exe(COMMANDS.get("product_version")).strip()
        if self.node_type in [QPLUS]:
            return self.exe(COMMANDS.get("qplus_version")).strip()

    def get_system(self):
        """客户业务系统"""
        return CONF.get("system")

    def get_size(self):
        """产品规模"""
        if self.node_type in [QPLUS]:
            return QPLUS
        if self.node_type in [SANFREE]:
            return "1+1"
        if self.node_type in [COMPUTE, STORAGE]:
            cluster = json.loads(self.exe(COMMANDS.get("qdatamgr_conf_show_s")))
            com = 0
            sto = 0
            for node in cluster:
                if node.get("type") == COMPUTE:
                    com += 1
                if node.get("type") == STORAGE:
                    sto += 1
            return f"{com}+{sto}"

    def get_sow(self):
        """sow含义暂不明确"""
        # FIXME:
        return NA

    def get_sla(self):
        """sla含义暂不明确"""
        # FIXME:
        return NA

    def get_desc(self):
        """描述一般采集完成后手动填写"""
        return NA


class NodeCollector(BaseCollector):
    """
    节点信息sheet采集
    """
    model_class = NodeSheet
    serializer_class = NodeSerializer

    def get_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn")).strip()

    def get_type_(self):
        """节点类型"""
        return self.node_type

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_hostname(self):
        """节点名称"""
        return self.exe(COMMANDS.get("hostname")).strip()

    def get_product_sn(self):
        """产品序列号"""
        if self.node_type in [SANFREE, COMPUTE, STORAGE]:
            cluster = json.loads(self.exe(COMMANDS.get("qdatamgr_conf_show_s")))
            for node in cluster:
                return node.get("cluster_uuid")
        if self.node_type in [QPLUS]:
            info = json.loads(self.exe(COMMANDS.get("zstack_ctl_license")))
            return info.get("inventory", {}).get("serialNumber")

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_brand(self):
        """节点品牌"""
        return self.exe(COMMANDS.get("node_brand")).strip()

    def get_model(self):
        """节点型号"""
        return self.exe(COMMANDS.get("node_model")).strip()

    def get_raid(self):
        """RAID卡驱动"""
        return self.exe(COMMANDS.get("raid_driver")).strip()

    def get_ib(self):
        """IB卡驱动"""
        return self.exe(COMMANDS.get("ib_driver")).strip()

    def get_flash(self):
        """FLASH卡类型+驱动"""
        # FIXME: 暂未确定具体命令
        return NA

    def get_cpu_model(self):
        """cpu型号"""
        return self.exe(COMMANDS.get("cpu_model")).strip()

    def get_cpu_num(self):
        """cpu数量"""
        return self.exe(COMMANDS.get("cpu_num")).strip()

    def get_memory_size(self):
        """内存大小(GB)"""
        return self.exe(COMMANDS.get("memory_size")).strip()

    def get_memory_num(self):
        """内存个数"""
        return self.exe(COMMANDS.get("memory_num")).strip()


class SoftwareCollector(BaseCollector):
    """
    软件信息sheet采集
    """
    model_class = SoftwareSheet
    serializer_class = SoftwareSerializer

    def get_sn(self):
        """软件序列号"""
        if self.node_type in [SANFREE, COMPUTE, STORAGE]:
            return self.exe(COMMANDS.get("software_sn")).strip()
        if self.node_type in [QPLUS]:
            info = json.loads(self.exe(COMMANDS.get("zstack_cli_license")))
            return info.get("inventory", {}).get("serialNumber")

    def get_node_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn")).strip()

    def get_order(self):
        """订单号"""
        return CONF.get("order")


class DiskOutputCollector(BaseCollector):
    """
    硬盘输出sheet采集
    """
    model_class = DiskOutputSheet
    serializer_class = DiskOutputSerializer

    def get_ip(self):
        """节点ip"""
        return self.ip

    def get_output(self):
        """磁盘输出"""
        if self.node_type in [SANFREE, COMPUTE, STORAGE]:
            return self.exe(COMMANDS.get("qdata_disk_output")).strip()
        if self.node_type in [QPLUS]:
            return self.exe(COMMANDS.get("qplus_disk_output")).strip()


class HardwareCollector(BaseCollector):
    """
    硬件信息sheet采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    @property
    def show_disk_p(self):
        """
        减少执行命令的次数，此处使用变量来保存一些结果
        """
        if "show_disk_p" not in self.data:
            self.data["show_disk_p"] = json.loads(self.exe(COMMANDS.get("qdatamgr_media_show_disk_p")))
        return self.data["show_disk_p"]

    @property
    def collect_disk_info_i(self):
        """
        磁盘信息保存
        """
        if "collect_disk_info_i" not in self.data:
            self.data["collect_disk_info_i"] = json.loads(self.exe(COMMANDS.get("qdatamgr_collect_disk_info_i")))
        return self.data["collect_disk_info_i"]

    @property
    def show_nvme(self):
        """
        nvme信息
        """
        if "show_nvme" not in self.data:
            self.data["show_nvme"] = json.loads(self.exe(COMMANDS.get("qdatamgr_media_show_nvme")))
        return self.data["show_nvme"]

    def collect(self, exclude=("id",)):
        # 首先获取每一类硬件资源列表, 给每一个硬件资源指定一个编号来进行采集
        devs = self.get_ssd_and_hdd()
        nvme = self.get_nvme()
        raid = self.get_raid()
        flash = self.get_flash()
        switch = self.get_switch()
        hca = self.get_hca()
        # 根据每个硬件实例的编号进行实例化
        collect_only([HDDSSDCollector(
            self.ip, self.node_type, dev_id,
            data={
                "show_disk_p": self.show_disk_p,
                "collect_disk_info_i": self.collect_disk_info_i,
            }) for dev_id in devs
        ])
        collect_only([NVMECollector(
            self.ip, self.node_type, nvme_id,
            data={
                "nvmes": self.show_nvme,
            }) for nvme_id in nvme
        ])
        collect_only([RaidCollector(self.ip, self.node_type, raid_id) for raid_id in raid])
        collect_only([FlashCollector(self.ip, self.node_type, flash_id) for flash_id in flash])
        if CONF.get("is_collect_switch", False):
            collect_only([SwitchCollector(self.ip, self.node_type, switch_id) for switch_id in switch])
        collect_only([HCACollector(self.ip, self.node_type, hca_id) for hca_id in hca])

    def get_ssd_and_hdd(self):
        """可选择 media show_disk
        注意点:
            - media show 和 collect disk_info 查看到的hdd和ssd都是本机物理磁盘, slot号最后两位是MegaCli中device_id
            所以此处使用slot号来对每一块磁盘进行区分
        """
        return [disk["Slot"] for disk in self.show_disk_p]

    def get_nvme(self):
        """
        有几个注意点:
            - 计算节点有可能存在nvme磁盘， 但多数情况下都是从存储传输上来的
            - 计算节点看到的nvme如果是从存储节点传输，则nvme list 中 model显示为Linux
            - media show 或者 media show_nvme 查看到的nvme一定是本机物理设备
            - collect_disk info -i 查看到的ssd和hdd为本地物理磁盘, nvme磁盘则可能是本地磁盘 + 远程磁盘
            - 有些nvme磁盘无法通过  lspci |grep -i nvme 查找到
            - 存储节点的普通磁盘可以通过nvmf协议挂载到计算节点，此时在计算节点看到的时一个nvme设备
        综上所述：
            - 采集时使用media show_nvme不区分节点跑一次，可保证nvme磁盘不漏不重
        """
        # 表的第一列明明是 /dev/nvme0n1  这样的盘符， 但是表头叫 Node， 历史原因...
        return [nvme["Node"] for nvme in self.show_nvme]

    def get_raid(self):
        """获取raid数量即可"""
        num = int(self.exe(COMMANDS.get("raid_num_fmt", "%s-%s") % (self.megacli_bin, "All")).strip())
        return [i for i in range(num)]

    def get_flash(self):
        # todo
        return []

    def get_switch(self):
        # todo
        return []

    def get_hca(self):
        # 获取所有hca卡的编号: 41:00.1
        out = self.exe(COMMANDS.get("hca_slot"))
        lines = out.splitlines()
        return [line.strip() for line in lines if line]


class HDDSSDCollector(BaseCollector):
    """
    SSD磁盘和HDD磁盘信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_disk_by_device_num(self):
        """
        根据逻辑盘符获取对应磁盘在MegaCli中的输出信息
        #MegaCli -pdinfo -PhysDrv[32:01] -a0

            Enclosure Device ID: 32
            Slot Number: 1
            Drive's position: DiskGroup: 0, Span: 0, Arm: 1
            Enclosure position: 1
            Device Id: 1
            WWN: 55cd2e414ec1d687
            Sequence Number: 2
            Media Error Count: 0
            Other Error Count: 0
            Predictive Failure Count: 0
            Last Predictive Failure Event Seq Number: 0
            PD Type: SATA

            Raw Size: 372.611 GB [0x2e9390b0 Sectors]
            Non Coerced Size: 372.111 GB [0x2e8390b0 Sectors]
            Coerced Size: 372.0 GB [0x2e800000 Sectors]
            Sector Size:  0
            Firmware state: Online, Spun Up
            Device Firmware Level: 0160
            Shield Counter: 0
            Successful diagnostics completion on :  N/A
            SAS Address(0): 0x4433221105000000
            Connected Port Number: 2(path0)
            Inquiry Data: BTHV74100DE1400NGN  INTEL SSDSC2BA400G4                     G2010160
            FDE Capable: Not Capable
            FDE Enable: Disable
            Secured: Unsecured
            Locked: Unlocked
            Needs EKM Attention: No
            Foreign State: None
            Device Speed: 6.0Gb/s
            Link Speed: 6.0Gb/s
            Media Type: Solid State Device
            Drive:  Not Certified
            Drive Temperature :23C (73.40 F)
            PI Eligibility:  No
            Drive is formatted for PI information:  No
            PI: No PI
            Drive's NCQ setting : N/A
            Port-0 :
            Port status: Active
            Port's Linkspeed: 6.0Gb/s
            Drive has flagged a S.M.A.R.T alert : No

            Exit Code: 0x00
        """
        output = ""
        pattern = re.compile(r"^P(\d+)B(\d+)S(\d+)$")

        # 将盘符中携带的 Enclosure 值和 Slot 号取出来
        match = pattern.search(self.hardware_id)
        if not match:
            return output
        _, enclosure_value, slot = match.groups()

        # 通过 MegaCLIBase 获取 collectors、 disks 信息
        mega = MegaCLIBase(self.megacli_bin, logger, self.ssh)
        mega.run_command(COMMANDS.get("pdlist_all"))
        for controller in mega.controllers:
            device_id = self.exe(
                COMMANDS.get("encinfo_fmt", "%s-%d") % (
                    self.megacli_bin,
                    controller.controller_number
                )
            ).strip()
            for disk in controller.PDs:
                # 判断为当前磁盘
                if disk.enclosure_id == device_id and disk.slot_number == slot:
                    return disk
        return None

    def get_type_(self):
        """磁盘类型"""
        for disk in self.data.get("show_disk_p", []):
            if disk["Slot"] == self.hardware_id:
                return disk["Type"]
        return NA

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_model(self):
        """磁盘型号"""
        for disk in self.data.get("show_disk_p", []):
            if disk["Slot"] == self.hardware_id:
                fields = disk["InqueryData"].split()
                if len(fields) > 0:
                    return f"{fields[0]} {disk['Interface']} {disk['Size']}"
        return NA

    def get_brand(self):
        """磁盘品牌"""
        for disk in self.data.get("show_disk_p", []):
            if disk["Slot"] == self.hardware_id:
                fields = disk["InqueryData"].split()
                if len(fields) > 0:
                    return fields[0]
        return NA

    def get_sn(self):
        """磁盘序列号"""
        devs = self.data.get("collect_disk_info_i", {})
        for dev in devs:
            if self.hardware_id in devs[dev]["device_name"]:
                return devs[dev]["serial_number"]
        return NA

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_firmware(self):
        """固件版本"""
        firmware = NA
        devs = self.data.get("collect_disk_info_i", {})
        for dev in devs:
            if self.hardware_id in devs[dev]["device_name"]:
                firmware = devs[dev]["firmware_version"]
                break
        if not firmware:
            # 尝试从MegaCli获取
            logger.info("Try to find firmware in Megacli output.")
            disk = self.get_disk_by_device_num()
            if disk:
                return disk.props.get("Device Firmware Level", NA)
        return firmware

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn"))


class SwitchCollector(BaseCollector):
    """
    IB交换机信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_type_(self):
        """配件类型"""
        # todo

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_model(self):
        """配件型号"""
        # todo

    def get_brand(self):
        """配件品牌"""
        # todo

    def get_sn(self):
        """配件序列号"""
        # todo

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_firmware(self):
        """固件版本"""
        # todo

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        # todo


class NVMECollector(BaseCollector):
    """
    NVME磁盘信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_type_(self):
        """配件类型"""
        return "NVME"

    def get_is_woqu_maintenance(self):
        """是否属沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance ", False))

    def get_model(self):
        """型号"""
        for nvme in self.data.get("nvmes", []):
            if nvme["Node"] == self.hardware_id:
                return nvme["Model"]
        return NA

    def get_brand(self):
        """配件品牌"""
        return self.exe(COMMANDS.get("nvme_brand"))

    def get_sn(self):
        """配件序列号"""
        for nvme in self.data.get("nvmes", []):
            if nvme["Node"] == self.hardware_id:
                return nvme["SN"]
        return NA

    def get_order(self):
        """订单号"""
        return CONF.get("order", NA)

    def get_firmware(self):
        """固件版本"""
        for nvme in self.data.get("nvmes", []):
            if nvme["Node"] == self.hardware_id:
                return nvme["FW Rev"]
        return NA

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn"))


class RaidCollector(BaseCollector):
    """
    RAID信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_type_(self):
        """配件类型
        """
        return "RAID"

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_model(self):
        """配件型号
            产品名称(容量)电池类型[电池数量]
        """
        product = self.exe(COMMANDS.get("raid_product_fmt") % (self.megacli_bin, self.hardware_id)).strip()
        size = self.exe(COMMANDS.get("raid_memory_size_fmt") % (self.megacli_bin, self.hardware_id)).strip()
        battery_type = self.exe(COMMANDS.get("raid_battery_type_fmt") % (self.megacli_bin, self.hardware_id)).strip()
        battery_num = self.exe(COMMANDS.get("raid_battery_num_fmt") % (self.megacli_bin, self.hardware_id)).strip()
        return f"{product}({size}){battery_type}[{battery_num}]"

    def get_brand(self):
        """配件品牌"""
        return "LSI"

    def get_sn(self):
        """配件序列号"""
        return self.exe(COMMANDS.get("raid_sn_fmt") % (self.megacli_bin, self.hardware_id)).strip()

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_firmware(self):
        """固件版本"""
        return self.exe(COMMANDS.get("raid_firmware_fmt") % (self.megacli_bin, self.hardware_id)).strip()

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn"))


class FlashCollector(BaseCollector):
    """
    flash信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_type_(self):
        """配件类型"""
        # todo

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_model(self):
        """配件型号"""
        # todo

    def get_brand(self):
        """配件品牌"""
        # todo

    def get_sn(self):
        """配件序列号"""
        # todo

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_firmware(self):
        """固件版本"""
        # todo

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        # todo


class HCACollector(BaseCollector):
    """
    HCA卡信息采集
    """
    model_class = HardwareSheet
    serializer_class = HardwareSerializer

    def get_type_(self):
        """配件类型"""
        return "HCA"

    def get_is_woqu_maintenance(self):
        """是否属于沃趣维保"""
        return yes_or_no(CONF.get("is_woqu_maintenance", False))

    def get_model(self):
        """配件型号"""
        return self.exe(COMMANDS.get("hca_model") % self.hardware_id).strip()

    def get_brand(self):
        """配件品牌"""
        return "Mellanox"

    def get_sn(self):
        """配件序列号"""
        return self.exe(COMMANDS.get("hca_sn") % self.hardware_id).strip()

    def get_order(self):
        """订单号"""
        return CONF.get("order")

    def get_firmware(self):
        """固件版本"""
        return self.exe(COMMANDS.get("hca_firmware")).strip()

    def get_is_produced_by_server(self):
        """是否随服务器采购"""
        return yes_or_no(CONF.get("is_produced_by_server", False))

    def get_node_sn(self):
        """节点序列号"""
        return self.exe(COMMANDS.get("node_sn"))
