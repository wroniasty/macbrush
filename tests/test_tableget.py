__author__ = 'wroniasty'

import unittest
import logging

from macbrush import tables

logging.basicConfig()


class TablesCase(unittest.TestCase):

    def test_table_object(self):

        class TestTable(tables.Table, tables.IntegerTableIndex):

            _IndexSize = 1

            Field1 = tables.TableField(1)
            Field2 = tables.TableIntegerField(2)
            Field3 = tables.TableMACField(3)

            def __init__(self):
                super(TestTable, self).__init__((1,3,6))

        table = TestTable()

        table.insert((1,3,6,1,1), "TEST_VALUE")
        table.insert((1,3,6,2,2), "65535")
        table.insert((1,3,6,3,3), "123456")

        self.assertTrue((1,3,6,2,2,2) in table)
        self.assertFalse((1,5,6,2,2,2) in table)
        self.assertFalse((1,3) in table)
        self.assertRaises(Exception, lambda: None in table)

        self.assertTrue(table.results[1]["Field1"] == "TEST_VALUE")
        self.assertTrue(table.results[2]["Field2"] == 65535)
        self.assertTrue(table.results[3]["Field3"] == "313233343536")


if __name__ == '__main__':
    unittest.main()
