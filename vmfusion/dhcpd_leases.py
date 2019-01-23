import os
from datetime import datetime
from typing import Dict, KeysView, Any

import pyparsing


class DHCPDLeases(object):
    """A dhcpd_leases contains a mapping between MAC and IP addresses from the
    content of a given dhpcd.leases file.

    When the lease file contains multiple leases for the same mac address, the
    lease with the latest start date is used."""

    def __init__(self, lease_file: str):
        if not os.path.isfile(lease_file):
            raise ValueError("dhcpd.leases '{0}' not found".format(lease_file))

        self.lease_file: str = lease_file
        self.list: Dict = {}

    def __parse(self):
        lbrace, rbrace, semi, quote = map(pyparsing.Suppress, '{};"')
        ip_address = pyparsing.Combine(pyparsing.Word(pyparsing.nums) + ('.' + pyparsing.Word(pyparsing.nums)) * 3)
        hex_int = pyparsing.Word(pyparsing.hexnums, exact=2)
        mac_address = pyparsing.Combine(hex_int + (':' + hex_int) * 5)
        hdw_type = pyparsing.Word(pyparsing.alphanums)
        yyyy_mm_dd = pyparsing.Combine((pyparsing.Word(pyparsing.nums, exact=4) |
                                        pyparsing.Word(pyparsing.nums, exact=2)) +
                                       ('/' + pyparsing.Word(pyparsing.nums, exact=2)) * 2)
        hh_mm_ss = pyparsing.Combine(pyparsing.Word(pyparsing.nums, exact=2) +
                                     (':' + pyparsing.Word(pyparsing.nums, exact=2)) * 2)
        date_ref = pyparsing.oneOf(list("0123456"))("weekday") + yyyy_mm_dd("date") + hh_mm_ss("time")

        def to_datetime(tokens):
            tokens["datetime"] = datetime.strptime("%(date)s %(time)s" % tokens, "%Y/%m/%d %H:%M:%S")

        date_ref.setParseAction(to_datetime)
        starts_stmt = "starts" + date_ref + semi
        ends_stmt = "ends" + (date_ref | "never") + semi
        tstp_stmt = "tstp" + date_ref + semi
        tsfp_stmt = "tsfp" + date_ref + semi
        hdw_stmt = "hardware" + hdw_type("type") + mac_address("mac") + semi
        uid_stmt = "uid" + pyparsing.QuotedString('"')("uid") + semi
        binding_stmt = "binding" + pyparsing.Word(pyparsing.alphanums) + pyparsing.Word(pyparsing.alphanums) + semi
        lease_statement = starts_stmt | ends_stmt | tstp_stmt | tsfp_stmt | hdw_stmt | uid_stmt | binding_stmt
        lease_def = "lease" + ip_address("ipaddress") + lbrace + \
                    pyparsing.Dict(pyparsing.ZeroOrMore(pyparsing.Group(lease_statement))) + rbrace

        with open(self.lease_file, 'r') as file:
            parsed = lease_def.scanString(file.read())

            return parsed

    def load(self):
        all_leases = {}

        for lease, start, stop in self.__parse():
            try:
                mac = lease.hardware.mac

                if mac not in all_leases or lease.starts.datetime > all_leases[mac].starts.datetime:
                    all_leases[mac] = lease

            except AttributeError as e:
                print(e)

        for mac in all_leases:
            all_leases[mac] = all_leases[mac].ipaddress

        self.list = all_leases

    reload = load

    def __len__(self) -> int:
        return len(self.list)

    def __iter__(self) -> KeysView:
        return self.list.keys()

    def __getitem__(self, item) -> Any:
        return self.list[item]

    def __contains__(self, item) -> bool:
        return item in self.list

    def __str__(self) -> str:
        return str(self.list)

    def __repr__(self) -> str:
        return repr(self.list)
