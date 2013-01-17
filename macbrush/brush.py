__author__ = 'wroniasty'

import tables


class IfTable(tables.Table, tables.IntegerTableIndex):

    Index = tables.TableIntegerField(1)
    Descr = tables.TableField(2)
    Type = tables.TableIntegerField(3)
    Mtu = tables.TableIntegerField(4)
    Speed = tables.TableIntegerField(5)
    PhysAddress = tables.TableMACField(6)
    AdminStatus = tables.TableIntegerField(7)
    OperStatus = tables.TableIntegerField(8)
    LastChange = tables.TableIntegerField(9)
    InOctets = tables.TableIntegerField(10)
    InUcastPkts = tables.TableIntegerField(11)
    InNUcastPkts = tables.TableIntegerField(12)
    InDiscards = tables.TableIntegerField(13)
    InErrors = tables.TableIntegerField(14)
    InUnknownProtos = tables.TableIntegerField(15)
    OutOctets = tables.TableIntegerField(16)
    OutUcastPkts = tables.TableIntegerField(17)
    OutNUcastPkts = tables.TableIntegerField(18)
    OutDiscards = tables.TableIntegerField(19)
    OutErrors = tables.TableIntegerField(20)
    OutUnknownProtos = tables.TableIntegerField(21)
    Specific = tables.TableIntegerField(22)

    def __init__(self):
        super(IfTable, self).__init__((1,3,6,1,2,1,2,2,1))


class FdbTable(tables.Table, tables.MACTableIndex):

    _IndexSize = 6

    PhysAddress = tables.TableMACField(1)
    Port = tables.TableIntegerField(2)
    Status = tables.TableIntegerField(3)

    def __init__(self):
        super(FdbTable, self).__init__((1,3,6,1,2,1,17,4,3,1))


class Dot1dBasePort(tables.Table, tables.IntegerTableIndex):

    _IndexSize = 1

    Port = tables.TableIntegerField(1)
    IfIndex = tables.TableIntegerField(2)


    def __init__(self):
        super(Dot1dBasePort, self).__init__((1,3,6,1,2,1,17,1,4,1))
