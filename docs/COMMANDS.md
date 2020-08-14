采集脚本用到的命令
---

## 测试验证机器

- Stand: 10.10.100.12
- Lite: 10.10.90.154
- QPlus: 10.10.60.41

## proinfo

- 产品序列号

**Stand**: 读取/home/sendoh/qdatamgr/Data/qdata.db中server表最后一列cluster_uuid值

**Lite**: 同stand

```
sqlite> select * from server;
san4|1|10.10.90.154|sanfree|172.16.128.154,172.16.129.154|QD-00041N23
san5|2|10.10.90.155|sanfree|172.16.129.155,172.16.128.155|QD-00041N23
```

**QPlus**: 执行zstack-cli 命令，获取其中SN字段

```
$zstack-cli 'GetQLisenceInfo'
{
    "inventory": {
        "exModule": [],
        "format": "{"storeCondtion":"200G","smallStoreRatio":1,"bigStoreCount":50,"backupDB":true,"timePoint":true,"identity":true,"monitor":true,"platform":true,"resource":true,"scheduler":true,"networkConfig":true,"nas":true,"disasterRecovery":true,"snapshotPoint":true,"compression":true,"customTask":true,"oracleModule":true,"mysqlModule":true,"sqlserverModule":true}",
        "hostCount": 1,
        "macAddress": "fa:c6:8f:a0:00:00",
        "nicName": "eth0",
        "notAllowAPIMessages": [],
        "serialNumber": "111",
        "type": "Trial",
        "validityPeriod": 1596697960513
    },
    "success": true
}
```

- 产品类型

```
qdatamgr conf show -s 取 type 一列
```

- type in [compute, storage] 判定产品类型为Standard
- type in [sanfree] 判定为Lite
- 命令错误或其他情况判定为QPlus


- 产品版本

**Stand**: 读取/etc/version.cfg中QData_version值，即cobbler版本

**Lite**: 同Stand

```
#cat /etc/version.cfg
[bundle_version]
QData_version = release-7.1.2
[ QData_For_Oracle ]
[name] - [release] - [commit-id]
qdata-qlink - v5.0.2 - d140b3a
oracle-oneclick - master - 5312b5e51e
qdata-mgr-env - release-6.2.0 - b09f202
qdata-mgr - release-7.1.2 - 85f78b5046
path_checker - master - cfd0f1a
qflame-release - release-1.4.2-infinite - a5787e7f
qdata-qlockdeploy - release-2.0.0 - 1c70771
qcollect - release-1.0.0--6.2.0 - 0e49dc9d7
qcheck - qcheck-2.0-qdatamgr-7.0.1 - 45d817ed
```

**QPlus**: 读取/etc/QPLUS_VERSION中第一行的值

```
$cat /etc/QPLUS_VERSION
5.1.3.2
ZStack:651f358
QStack:6c35781
QPlus:554def5
Utility:014e8c5
VmAgent:6695e13
```

- 业务系统

脚本执行前手工填写配置

- 产品规模

原本由脚本运行前手工填写

> 优化: Stand和Lite 统计 qdatamgr conf show -s 中节点类型数量, QPlus 默认为 1

- SOW

**不清楚此项含义，且取值总是N/A**

- SLA

**不清楚此项含义，且取值总是N/A**

- 产品说明

默认为N/A，如需特殊说明，脚本跑完后手工在excel填写

## 节点

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $2}'
# 37Z9D53
# 5cda2c45-b091-4485-b6bd-5cad3808ad0d
```

- 节点类型

**Stand&Lite**
```
cat /root/qdata/node_type.csv
```

**QPlus:** N/A

- 是否属于沃趣维保

执行脚本前手动填写配置

- 主机名称

```
hostname
```

- 产品序列号

同proinfo中获取产品序列号

- 订单号

运行脚本之后前或之后手动填写

- 节点品牌

```
dmidecode -t 1|grep Manufacturer|awk -F ':' '{print $2}'
```

- 节点型号

```
dmidecode -t 1|grep Product|awk -F ':' '{print $2}
```

- RAID卡驱动

```
modinfo megaraid_sas|grep ^version|awk '{print $2}'
```

- IB卡驱动

```
ibstat |grep -i "Firmware version:"|head -n 1|awk -F ":" '{print $2}'
```

- FLASH卡驱动

**命令在机器上没有找见**

```
fio-status -v
# 或者
shannon-status -v
```

- CPU型号

```
cat /proc/cpuinfo |grep model|sort -n|uniq -c|grep name|awk -F":" '{print $2}'
```

- CPU个数

```
cat /proc/cpuinfo |grep "physical id"|sort |uniq|wc -l
```

- 内存大小(GB)

```
free -g|grep Mem|awk '{print $2}'
```

- 内存个数

```
dmidecode|grep -A5 "Memory Device"|grep Size|grep -v Range|grep -v No|wc -l
```

## 硬件

> 此部分为采集关键

### SWITCH

- 配件类型

SWITCH

- 是否属沃趣维保

运行脚本前手动填写或运行完修改

- 型号

```
show inventory|include CHASS
show hosts|include Hostname
```

- 配件品牌

- 配件序列号

- 订单号

- 固件版本

- 是否随服务器采购

- 节点序列号

### HDD

- 配件类型

HDD

- 是否属沃趣维保

运行脚本前手动填写配置

- 型号

**Stand & Lite**: 取 `InqueryData` 第一段，`Interface`，`Size` 三段拼接而成
```
qdatamgr media show_disk -p
+----------+----------+-----------+------+------------------+---------------+-----------------------------------+
|   Slot   |   Size   | Interface | Type |       WWN        | Foreign_State |            InqueryData            |
+==========+==========+===========+======+==================+===============+===================================+
| P5B00S00 | 1.090 TB | SAS       | HDD  | 5000C500CA4951C8 | None          | SEAGATE ST1200MM0099 ST33WFK7S0V8 |
+----------+----------+-----------+------+------------------+---------------+-----------------------------------+
| P5B00S01 | 1.090 TB | SAS       | HDD  | 5000C500CA493CD4 | None          | SEAGATE ST1200MM0099 ST33WFK73XXF |
+----------+----------+-----------+------+------------------+---------------+-----------------------------------+
```

- 配件品牌

`InqueryData` 第一段

- 配件序列号

`InqueryData` 倒数第二段

- 订单号

采集脚本运行之前或之后手动填写配置

- 固件版本

```
# P0B00S01

MegaCli -EncInfo -a0

    Number of enclosures on adapter 0 -- 1

    Enclosure 0:
    Device ID                     : 32
    Number of Slots               : 8
    Number of Power Supplies      : 0
    Number of Fans                : 0
    Number of Temperature Sensors : 0

根据此 -a0 (controller_id) 获取到 Enclosure 值和Device ID 的关系, Enclosure 值即为 B00 后的编号, S01为 Slot号

MegaCli -pdinfo -PhysDrv[32:01] -a0   # 其中 [DeviceID:Slot]  -a0 为 collector_id

查找到对应磁盘输出的Megacli信息

```

- 是否随服务器采购

运行脚本之前手动填写配置

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $2}'
```

### SSD

同HDD

### NVME

- 配件类型

NVME

- 是否属于沃趣维保

脚本运行之前手动填写配置

- 型号

```
qdatamgr media show_nvme 取 Model 列
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
|     Node     |         SN         |  Size  |                  Model                   | Namespace |  FW Rev  | Format |   partitions   |
+==============+====================+========+==========================================+===========+==========+========+================+
| /dev/nvme0n1 | PHLF8125026D1P0GGN | 1.00TB | INTEL SSDPE2KX010T7                      | 1         | QDV101D1 | 512B   | /dev/nvme0n1p1 |
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
| /dev/nvme1n1 | PHLF8132006B1P0GGN | 1.00TB | INTEL SSDPE2KX010T7                      | 1         | QDV101D1 | 512B   | /dev/nvme1n1p1 |
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
| /dev/nvme2n1 | PHLF8125026C1P0GGN | 1.00TB | INTEL SSDPE2KX010T7                      | 1         | QDV101D1 | 512B   | /dev/nvme2n1p1 |
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
| /dev/nvme3n1 | PHLF812502HJ1P0GGN | 1.00TB | INTEL SSDPE2KX010T7                      | 1         | QDV101D1 | 512B   | /dev/nvme3n1p1 |
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
| /dev/nvme5n1 | PHLF8125026P1P0GGN | 1.00TB | INTEL SSDPE2KX010T7                      | 1         | QDV101D1 | 512B   | /dev/nvme5n1p1 |
+--------------+--------------------+--------+------------------------------------------+-----------+----------+--------+----------------+
```

- 配件品牌

```
lspci |grep -i non |awk -F ' ' '{print $5 " " $6}'|tail -n 1
```

- 配件序列号

```
# 取nvme序号
lspci |grep -i Mellanox|awk '{print $1}'|awk -F "." '{print $1}'

# 根据序号取SN
lspci -vvv -s <num:num>|grep SN|awk -F ":" '{print $2}'
```

- 订单号

运行脚本前手动填写配置

- 固件版本: 取nvme list 最后一列

```
nvme list|grep <nvme_path>|awk '{print $NF}'
```

- 是否随服务器采购

运行脚本前手动填写配置

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $2}'
```

### RAID

- 配件类型

RAID

- 是否属于沃趣维保

运行脚本前手动填写配置

- 型号: 产品名称(容量)BBU「电池数量」

```
# 获取raid数量
MegaCli -AdpAllInfo -aALL |grep "Serial No"|wc -l

# 按照数量序号取信息
[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'Product'
# Product Name    : PERC H740P Adapter

# 获取产品名称
[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'Product'|awk -F ":" '{print $2}'
# PERC H740P Adapter

[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'Memory Size'
# Memory Size      : 8192MB

# 获取容量大小
[root@qdata-sto12 /root]
#MegaCli -AdpAllInfo -a0|grep 'Memory Size'|awk -F ":" '{print $2}'
 8192MB

[root@qdata-sto12 /root]
MegaCli -AdpBbuCmd -GetBbuStatus -a0|grep "BatteryType"
# BatteryType: BBU

# 获取电池数量
[root@qdata-sto12 /root]
MegaCli -AdpBbuCmd -GetBbuStatus -a0|grep "BatteryType"|wc -l
# 1
```

- 配件品牌

固定为 `LSI`， 未执行任何命令

- 配件序列号

```
# 获取raid数量
MegaCli -AdpAllInfo -aALL |grep "Serial No"|wc -l

# 按照数量序号取信息 -a<num>
[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'Serial No'
# Serial No       : 04B01VZ

[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'Serial No'|awk -F ":" '{print $NF}'
# 04B01VZ
```

- 订单号

运行脚本前手动填写配置

- 固件版本

```
# 获取raid数量
MegaCli -AdpAllInfo -aALL |grep "Serial No"|wc -l

# 根据数量编号获取信息 -a<num>
[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'FW'
#FW Package Build: 50.9.4-3025
#FW Version         : 5.093.00-2856
#Current Size of FW Cache       : 6319 MB
#Support Online FW Update	: Yes

[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'FW Package Build'
#FW Package Build: 50.9.4-3025

[root@qdata-sto12 /root]
MegaCli -AdpAllInfo -a0|grep 'FW Package Build'|awk -F ":" '{print $NF}'
# 50.9.4-3025
```

- 是否随服务器采购

运行脚本前手动填写配置

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $NF}'
```

### HCA

- 配件类型

HCA

- 是否属于沃趣维保

运行脚本前手动填写配置

- 型号

```
# 获取hca卡数量
[root@qdata-sto12 /root]
lspci |grep Mellanox|grep -v Virtual|wc -l
# 1

lspci |grep Mellanox|grep -v Virtual
# 5e:00.0 Infiniband controller: Mellanox Technologies MT27500 Family [ConnectX-3]

# 按照数量顺序取信息 head -n <num>
[root@qdata-sto12 /root]
lspci |grep Mellanox|grep -v Virtual|awk '{print $1}'|head -n <num>|tail -n 1
# 5e:00.0

[root@qdata-sto12 /root]
#lspci -vvv -s 5e:00.0|grep 'PN'
			[PN] Part number: MCX354A-FCBT

# 获取part no
[root@qdata-sto12 /root]
#lspci -vvv -s 5e:00.0|grep 'PN'|awk -F ":" '{print $NF}'
 MCX354A-FCBT
```

- 配件品牌

固定为 `Mellanox`， 未执行任何命令

- 配件序列号

```
# 获取编号
[root@qdata-sto12 /root]
lspci |grep Mellanox|grep -v Virtual|awk '{print $1}'|head -n 1|tail -n 1
#5e:00.0

[root@qdata-sto12 /root]
#lspci -vv -s 5e:00.0|grep 'SN'
			[SN] Serial number: MT1411X04983

# 根据pci编号获取SN
[root@qdata-sto12 /root]
#lspci -vv -s 5e:00.0|grep 'SN'|awk -F ':' '{print $NF}'
 MT1411X04983
```

- 订单号

运行脚本前手动填写配置

- 固件版本

```
# 获取hca卡数量
[root@qdata-sto12 /root]
lspci |grep Mellanox|grep -v Virtual|wc -l
# 1

# 按照hca卡数量顺序取fw   head -n <num>
[root@qdata-sto12 /root]
ibv_devinfo |grep fw_ver|awk -F ':' '{print $NF}'|head -n <num>|tail -n 1
#2.42.5000
```

- 是否随服务器采购

运行脚本前手动填写配置

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $NF}'
#  J40D143
```

### FLASH1(原脚本区分了flash1和flash2)

**fio-status**和**shannon-status**命令均未找见

- 配件类型

FLASH

- 是否属于沃趣维保

运行脚本前手动填写配置

- 型号

```
# 获取flash数量
fio-status -a|grep "Product Number"|grep "SN"|grep FIO|wc -l

# 按照数量顺序获取型号
fio-status -a|grep 'Product Number'|grep 'SN'|grep FIO|awk -F ',' '{print $1}'|awk '{print $2}'|head -n <num>|tail -n 1

# 或者
shannon-status -a|grep 'Product Model'|awk -F ':' '{print $2}'|head -n <num>|tail -n 1
```

- 配件品牌

```
fio-status -a|head -5|tail -n 1

# 命令有输出则为 "宝存"， 否则为 "闪迪"
```

- 配件序列号

```
# 获取flash数量
fio-status -a|grep "Product Number"|grep "SN"|grep FIO|wc -l

fio-status -a|grep 'Product Number'|grep 'SN'|grep FIO|awk -F ',' '{print $3}'|awk -F ':' '{print $2}'|head -n <num>|tail -n 1

# 或者
shannon-status -a|grep Ser|awk '{print $3}'|head -n <num>|tail -n 1
```

- 订单号

运行脚本前手动填写配置

- 固件版本

```
# 获取flash数量
fio-status -a|grep "Product Number"|grep "SN"|grep FIO|wc -l

fio-status -a|grep mware|awk -F ',' '{print $1}'|awk '{print $2}'|head -n <num>|tail -n 1

# 或者
shannon-status -a|grep 'Firmware Version'|awk '{print $3}'|head -n <num>|tail -n 1
```

- 是否随服务器采购

运行脚本前手动填写配置

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $NF}'
```

### FLASH2

- 配件类型

FLASH

- 是否属于沃趣维保

运行脚本前手动填写配置

- 型号: **除此项外，其余和flash1完全一致**

```
# 获取flash数量
shannon-status -a|grep "Product Model"|wc -l

# 之后逻辑同flash1
```

- 配件品牌
- 配件序列号
- 订单号
- 固件版本
- 是否随服务器采购
- 节点序列号

## 软件

- 软件序列号: **经过核查文件已经不存在**

```
cat /usr/local/sendoh/conf/qlink.sn
```

- 节点序列号

```
dmidecode -t 1|grep Serial|awk -F':' '{print $NF}'
```

- 订单号

运行脚本前手动填写配置

## 硬盘输出详情

- IP

Stand & Lite
```
/usr/local/bin/api-qdatamgr conf show -s 中节点ip信息
```

QPlus
```
hostname -I
```

- 硬盘输出

**QData**

```
[root@qdata-sto12 /usr/local/sendoh/conf]
MegaCli -PDList -aAll |grep 'Inquiry'
#Inquiry Data: TOSHIBA AL15SEB120NY    EF0540L0A0S8FQVF
#Inquiry Data: TOSHIBA AL15SEB120NY    EF0540L0A0T5FQVF

[root@qdata-sto12 /usr/local/sendoh/conf]
MegaCli -PDList -aAll |grep 'Inquiry'|awk -F ":" '{print $NF}'
# TOSHIBA AL15SEB120NY    EF0540L0A0S8FQVF
# TOSHIBA AL15SEB120NY    EF0540L0A0T5FQVF
```

**QPlus**

```
/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aAll |grep 'Inquiry'|awk -F ':' '{print $NF}'
```

