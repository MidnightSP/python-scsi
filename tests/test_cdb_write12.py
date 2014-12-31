#!/usr/bin/env python
# coding: utf-8

from pyscsi.pyscsi.scsi import SCSI
from pyscsi.pyscsi.scsi_enum_command import OPCODE
from pyscsi.utils.converter import scsi_ba_to_int


class MockWrite12(object):
    def execute(self, cdb, dataout, datain, sense):
        pass


def main():
    s = SCSI(MockWrite12())
    data = bytearray(27 * 512)

    w = s.write12(1024, 27, data)
    cdb = w.cdb
    assert cdb[0] == OPCODE.WRITE_12
    assert cdb[1] == 0
    assert scsi_ba_to_int(cdb[2:6]) == 1024
    assert scsi_ba_to_int(cdb[6:10]) == 27
    assert cdb[10] == 0
    assert cdb[11] == 0
    cdb = w.unmarshall_cdb(cdb)
    assert cdb['opcode'] == OPCODE.WRITE_12
    assert cdb['wrprotect'] == 0
    assert cdb['dpo'] == 0
    assert cdb['fua'] == 0
    assert cdb['lba'] == 1024
    assert cdb['group'] == 0
    assert cdb['tl'] == 27

    w = s.write12(65536, 27, data, wrprotect=2, dpo=1, fua=1, group=19)
    cdb = w.cdb
    assert cdb[0] == OPCODE.WRITE_12
    assert cdb[1] == 0x58
    assert scsi_ba_to_int(cdb[2:6]) == 65536
    assert scsi_ba_to_int(cdb[6:10]) == 27
    assert cdb[10] == 0x13
    assert cdb[11] == 0
    cdb = w.unmarshall_cdb(cdb)
    assert cdb['opcode'] == OPCODE.WRITE_12
    assert cdb['wrprotect'] == 2
    assert cdb['dpo'] == 1
    assert cdb['fua'] == 1
    assert cdb['lba'] == 65536
    assert cdb['group'] == 19
    assert cdb['tl'] == 27

if __name__ == "__main__":
    main()

