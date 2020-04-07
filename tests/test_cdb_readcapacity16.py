#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2014 by Ronnie Sahlberg <ronniesahlberg@gmail.com>
# Copyright (C) 2015 by Markus Rosjat <markus.rosjat@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from pyscsi.utils.converter import scsi_ba_to_int
from pyscsi.pyscsi.scsi_enum_command import sbc
from pyscsi.pyscsi.scsi_cdb_readcapacity16 import ReadCapacity16
from mock_device import MockDevice, MockSCSI


def main():

    with MockSCSI(MockDevice(sbc)) as s:
        r = s.readcapacity16(alloclen=37)
        cdb = r.cdb
        assert cdb[0] == s.device.opcodes.SBC_OPCODE_9E.value
        assert cdb[1] == s.device.opcodes.SBC_OPCODE_9E.serviceaction.READ_CAPACITY_16
        assert cdb[2:10] == bytearray(8)
        assert scsi_ba_to_int(cdb[10:14]) == 37
        assert cdb[14:16] == bytearray(2)
        cdb = r.unmarshall_cdb(cdb)
        assert cdb['opcode'] == s.device.opcodes.SBC_OPCODE_9E.value
        assert cdb['service_action'] == s.device.opcodes.SBC_OPCODE_9E.serviceaction.READ_CAPACITY_16
        assert cdb['alloc_len'] == 37

        d = ReadCapacity16.unmarshall_cdb(ReadCapacity16.marshall_cdb(cdb))
        assert d == cdb


if __name__ == "__main__":
    main()

