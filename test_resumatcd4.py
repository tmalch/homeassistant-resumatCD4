import unittest
from resumatcd4 import ResumatCD4
from crccheck.crc import Crc16Buypass


class TestResumatCD4(unittest.TestCase):
    def test_build_read_command(self):
        cd4 = ResumatCD4()
        res = cd4.build_read_command(0x0008, 0x0004)
        res2 = cd4.build_read_command(bytes.fromhex("0008"), bytes.fromhex("0004"))
        self.assertEqual(res, res2)


    def test_parse_read_response(self):
        cd4 = ResumatCD4()
        data = cd4.parse_read_response(b'\x10\x02\x00\x17f\x10\x10\xb6A\x10\x03\x0c\xce')
        self.assertEqual(data, b'f\x10\xb6A')

        data = cd4.parse_read_response(b'\x10\x02\x00\x17\x10\x10\xb6\x10\x10\x10\x03'+ Crc16Buypass.calcbytes(b'\x00\x17\x10\x10\xb6\x10\x10'))
        self.assertEqual(data, b'\x10\xb6\x10')

        data = cd4.parse_read_response(b'\x10\x02\x00\x17\x10\x10\x10\x10\x10\x03'+ Crc16Buypass.calcbytes(b'\x00\x17\x10\x10\x10\x10'))
        self.assertEqual(data, b'\x10\x10')


if __name__ == '__main__':
    unittest.main()
