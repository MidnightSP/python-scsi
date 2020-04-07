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

from mock_device import MockDevice, MockSCSI
from pyscsi.utils.converter import scsi_int_to_ba
from pyscsi.pyscsi.scsi_enum_command import smc
from pyscsi.pyscsi import scsi_enum_modesense as MODESENSE10
from pyscsi.pyscsi.scsi_cdb_modesense10 import ModeSense10


class MockModeSenseEAA(MockDevice):

    def execute(self, cmd):
        cmd.datain[0] = 21    # mode data length
        cmd.datain[2] = 97    # medium type
        cmd.datain[3] = 98    # device specific parameter
        cmd.datain[4] = 0x01  # LONGLBA
        cmd.datain[6] = 0     # block descriptor length

        cmd.datain[8] = 0x9d  # PS=1 SPF=0 PAGECODE=0x1d
        cmd.datain[9] = 16    # Parameter List Length

        cmd.datain[10:12] = bytearray([1, 1])  # First Medium Transfer Element
        cmd.datain[12:14] = bytearray([1, 2])  # Num Medium Transfer Elements
        cmd.datain[14:16] = bytearray([1, 3])  # First Storage Element
        cmd.datain[16:18] = bytearray([1, 4])  # Num Storage Elements
        cmd.datain[18:20] = bytearray([1, 5])  # First Import Element
        cmd.datain[20:22] = bytearray([1, 6])  # Num Import Elements
        cmd.datain[22:24] = bytearray([1, 7])  # First Data Transport Element
        cmd.datain[24:26] = bytearray([1, 8])  # Num Data Transport Elements


class MockModeSenseControl(MockDevice):

    def execute(self, cmd):
        cmd.datain[0] = 15    # mode data length
        cmd.datain[2] = 0     # medium type: BLOCK_DEVICE
        cmd.datain[3] = 0x90  # device specific parameter
        cmd.datain[6] = 0     # block descriptor length

        cmd.datain[8] = 0x8a  # PS=1 SPF=0 PAGECODE=0x0a
        cmd.datain[9] = 10    # Parameter List Length

        cmd.datain[10] = 0x9f  # tst:4 tmdf_only:1 dpicz:1 d_Sense:1 gltsd:1 rlec:1
        cmd.datain[11] = 0x9e  # qam:9 nuar:1 qerr:3
        cmd.datain[12] = 0xf8  # vs:1 rac:1 uaic:3 swp:1
        cmd.datain[13] = 0xf7  # ato:1 tas:1 atmpe:1 rwwp:1 am:7
        cmd.datain[16:18] = scsi_int_to_ba(500, 2)  # busy timeout:500
        cmd.datain[18:20] = scsi_int_to_ba(700, 2)  # ext:700


class MockModeSenseControlExt1(MockDevice):

    def execute(self, cmd):
        cmd.datain[0] = 15    # mode data length
        cmd.datain[2] = 0     # medium type: BLOCK_DEVICE
        cmd.datain[3] = 0x90  # device specific parameter
        cmd.datain[6] = 0     # block descriptor length

        cmd.datain[8] = 0xca                       # PS=1 SPF=1 PAGECODE=0x0a
        cmd.datain[9] = 1                          # subpage:1
        cmd.datain[10:12] = scsi_int_to_ba(0x1c, 2)  # page length

        cmd.datain[12] = 0x07  # tcmod:1 scsip:1 ialuae:1
        cmd.datain[13] = 0x0f  # icp:15
        cmd.datain[14] = 29   # msdl:29


class MockModeSenseDisconnect(MockDevice):

    def execute(self, cmd):
        cmd.datain[0] = 15    # mode data length
        cmd.datain[2] = 0     # medium type: BLOCK_DEVICE
        cmd.datain[3] = 0x90  # device specific parameter
        cmd.datain[6] = 0     # block descriptor length

        cmd.datain[8] = 0x82  # PS=1 SPF=0 PAGECODE=0x02
        cmd.datain[9] = 0x0e

        cmd.datain[10] = 122                          # bfr:122
        cmd.datain[11] = 123                          # ber:123
        cmd.datain[12:14] = scsi_int_to_ba(2371, 2)   # bil
        cmd.datain[14:16] = scsi_int_to_ba(2372, 2)  # dtl
        cmd.datain[16:18] = scsi_int_to_ba(2373, 2)  # ctl
        cmd.datain[18:20] = scsi_int_to_ba(2374, 2)  # mbs
        cmd.datain[20] = 0xff                        # emdp:1 fa:7 dimm:1 dtdc:7
        cmd.datain[22:24] = scsi_int_to_ba(2375, 2)  # fbs


def main():
    # SMC ElementAddressAssignment
    with MockSCSI(MockModeSenseEAA(smc)) as s:
        i = s.modesense10(page_code=MODESENSE10.PAGE_CODE.ELEMENT_ADDRESS_ASSIGNMENT).result
        assert i['medium_type'] == 97
        assert i['device_specific_parameter'] == 98

        assert len(i['mode_pages']) == 1

        assert i['mode_pages'][0]['ps'] == 1
        assert i['mode_pages'][0]['spf'] == 0
        assert i['mode_pages'][0]['page_code'] == MODESENSE10.PAGE_CODE.ELEMENT_ADDRESS_ASSIGNMENT
        assert i['mode_pages'][0]['first_medium_transport_element_address'] == 257
        assert i['mode_pages'][0]['num_medium_transport_elements'] == 258
        assert i['mode_pages'][0]['first_storage_element_address'] == 259
        assert i['mode_pages'][0]['num_storage_elements'] == 260
        assert i['mode_pages'][0]['first_import_element_address'] == 261
        assert i['mode_pages'][0]['num_import_elements'] == 262
        assert i['mode_pages'][0]['first_data_transfer_element_address'] == 263
        assert i['mode_pages'][0]['num_data_transfer_elements'] == 264

        d = ModeSense10.unmarshall_datain(ModeSense10.marshall_datain(i))
        assert d == i

        # SPC Control
        s.device = MockModeSenseControl(smc)
        i = s.modesense10(page_code=MODESENSE10.PAGE_CODE.CONTROL).result
        assert i['medium_type'] == 0
        assert i['device_specific_parameter'] == 0x90

        assert len(i['mode_pages']) == 1

        assert i['mode_pages'][0]['ps'] == 1
        assert i['mode_pages'][0]['spf'] == 0
        assert i['mode_pages'][0]['page_code'] == MODESENSE10.PAGE_CODE.CONTROL
        assert i['mode_pages'][0]['tst'] == 4
        assert i['mode_pages'][0]['tmf_only'] == 1
        assert i['mode_pages'][0]['dpicz'] == 1
        assert i['mode_pages'][0]['d_sense'] == 1
        assert i['mode_pages'][0]['gltsd'] == 1
        assert i['mode_pages'][0]['rlec'] == 1
        assert i['mode_pages'][0]['queue_algorithm_modifier'] == 9
        assert i['mode_pages'][0]['nuar'] == 1
        assert i['mode_pages'][0]['qerr'] == 3
        assert i['mode_pages'][0]['vs'] == 1
        assert i['mode_pages'][0]['rac'] == 1
        assert i['mode_pages'][0]['ua_intlck_ctrl'] == 3
        assert i['mode_pages'][0]['swp'] == 1
        assert i['mode_pages'][0]['ato'] == 1
        assert i['mode_pages'][0]['tas'] == 1
        assert i['mode_pages'][0]['atmpe'] == 1
        assert i['mode_pages'][0]['rwwp'] == 1
        assert i['mode_pages'][0]['autoload_mode'] == 7
        assert i['mode_pages'][0]['busy_timeout_period'] == 500
        assert i['mode_pages'][0]['extended_self_test_completion_time'] == 700

        d = ModeSense10.unmarshall_datain(ModeSense10.marshall_datain(i))
        assert d == i

        # SPC Control Ext 1
        s.device = MockModeSenseControlExt1(smc)
        i = s.modesense10(page_code=MODESENSE10.PAGE_CODE.CONTROL, sub_page_code=1).result
        assert i['medium_type'] == 0
        assert i['device_specific_parameter'] == 0x90

        assert len(i['mode_pages']) == 1

        assert i['mode_pages'][0]['ps'] == 1
        assert i['mode_pages'][0]['spf'] == 1
        assert i['mode_pages'][0]['page_code'] == MODESENSE10.PAGE_CODE.CONTROL
        assert i['mode_pages'][0]['sub_page_code'] == 1
        assert i['mode_pages'][0]['tcmos'] == 1
        assert i['mode_pages'][0]['scsip'] == 1
        assert i['mode_pages'][0]['ialuae'] == 1
        assert i['mode_pages'][0]['initial_command_priority'] == 15
        assert i['mode_pages'][0]['maximum_sense_data_length'] == 29

        d = ModeSense10.unmarshall_datain(ModeSense10.marshall_datain(i))
        assert d == i

        # SPC Disconnect
        s.device = MockModeSenseDisconnect(smc)
        i = s.modesense10(page_code=MODESENSE10.PAGE_CODE.DISCONNECT_RECONNECT).result
        assert i['medium_type'] == 0
        assert i['device_specific_parameter'] == 0x90

        assert len(i['mode_pages']) == 1

        assert i['mode_pages'][0]['ps'] == 1
        assert i['mode_pages'][0]['spf'] == 0
        assert i['mode_pages'][0]['page_code'] == MODESENSE10.PAGE_CODE.DISCONNECT_RECONNECT
        assert i['mode_pages'][0]['buffer_full_ratio'] == 122
        assert i['mode_pages'][0]['buffer_empty_ratio'] == 123
        assert i['mode_pages'][0]['bus_inactivity_limit'] == 2371
        assert i['mode_pages'][0]['disconnect_time_limit'] == 2372
        assert i['mode_pages'][0]['connect_time_limit'] == 2373
        assert i['mode_pages'][0]['maximum_burst_size'] == 2374
        assert i['mode_pages'][0]['emdp'] == 1
        assert i['mode_pages'][0]['fair_arbitration'] == 7
        assert i['mode_pages'][0]['dimm'] == 1
        assert i['mode_pages'][0]['dtdc'] == 7
        assert i['mode_pages'][0]['first_burst_size'] == 2375

        d = ModeSense10.unmarshall_datain(ModeSense10.marshall_datain(i))
        assert d == i


if __name__ == "__main__":
    main()


