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
from mock_device import MockDevice, MockSCSI
from pyscsi.pyscsi.scsi_cdb_getlbastatus import GetLBAStatus


def main():
    with MockSCSI(MockDevice(sbc)) as s:
        r = s.getlbastatus(19938722, alloclen=1112527)
        cdb = r.cdb
        assert cdb[0] == s.device.opcodes.SBC_OPCODE_9E.value
        assert cdb[1] == s.device.opcodes.SBC_OPCODE_9E.serviceaction.GET_LBA_STATUS
        assert scsi_ba_to_int(cdb[2:10]) == 19938722
        assert scsi_ba_to_int(cdb[10:14]) == 1112527
        assert cdb[14:16] == bytearray(2)
        cdb = r.unmarshall_cdb(cdb)
        assert cdb['opcode'] == s.device.opcodes.SBC_OPCODE_9E.value
        assert cdb['service_action'] == s.device.opcodes.SBC_OPCODE_9E.serviceaction.GET_LBA_STATUS
        assert cdb['lba'] == 19938722
        assert cdb['alloc_len'] == 1112527

        d = GetLBAStatus.unmarshall_cdb(GetLBAStatus.marshall_cdb(cdb))
        assert d == cdb


if __name__ == "__main__":
    main()


