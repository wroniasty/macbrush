__author__ = 'wroniasty'

import tables


class IfTable(tables.Table, tables.IntegerTableIndex):

    Index = tables.TableIntegerField(1)
    Desc = tables.TableField(2)
    Speed = tables.TableIntegerField(5)
    PhysAddress = tables.TableMACField(6)
    AdminStatus = tables.TableIntegerField(7)
    OperStatus = tables.TableIntegerField(8)
    LastChange = tables.TableIntegerField(9)

    def __init__(self):
        super(IfTable, self).__init__((1,3,6,1,2,1,2,2,1))


class FdbTable(tables.Table, tables.MACTableIndex):

    _IndexSize = 6

    PhysAddress = tables.TableMACField(1)
    Port = tables.TableIntegerField(2)
    Status = tables.TableIntegerField(3)

    def __init__(self):
        super(FdbTable, self).__init__((1,3,6,1,2,1,17,4,3,1))
