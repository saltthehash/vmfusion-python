import os
from datetime import datetime

from pyparsing import *


class DHCPDLeases(object):
    """A dhcpd_leases contains a mapping between MAC and IP addresses from the
    content of a given dhpcd.leases file.

    When the lease file contains multiple leases for the same mac address, the
    lease with the latest start date is used."""

    def __init__(self, lease_file):
        if not os.path.isfile(lease_file):
            raise ValueError("dhcpd.leases '{0}' not found".format(lease_file))

        self.lease_file = lease_file
        self.list = {}

    def __parse(self):
        LBRACE, RBRACE, SEMI, QUOTE = map(Suppress, '{};"')
        ipAddress = Combine(Word(nums) + ('.' + Word(nums)) * 3)
        hexint = Word(hexnums, exact=2)
        macAddress = Combine(hexint + (':' + hexint) * 5)
        hdwType = Word(alphanums)
        yyyymmdd = Combine((Word(nums, exact=4) | Word(nums, exact=2)) + ('/' + Word(nums, exact=2)) * 2)
        hhmmss = Combine(Word(nums, exact=2) + (':' + Word(nums, exact=2)) * 2)
        dateRef = oneOf(list("0123456"))("weekday") + yyyymmdd("date") + hhmmss("time")

        def to_datetime(tokens):
            tokens["datetime"] = datetime.strptime("%(date)s %(time)s" % tokens, "%Y/%m/%d %H:%M:%S")

        dateRef.setParseAction(to_datetime)
        startsStmt = "starts" + dateRef + SEMI
        endsStmt = "ends" + (dateRef | "never") + SEMI
        tstpStmt = "tstp" + dateRef + SEMI
        tsfpStmt = "tsfp" + dateRef + SEMI
        hdwStmt = "hardware" + hdwType("type") + macAddress("mac") + SEMI
        uidStmt = "uid" + QuotedString('"')("uid") + SEMI
        bindingStmt = "binding" + Word(alphanums) + Word(alphanums) + SEMI
        leaseStatement = startsStmt | endsStmt | tstpStmt | tsfpStmt | hdwStmt | uidStmt | bindingStmt
        leaseDef = "lease" + ipAddress("ipaddress") + LBRACE + Dict(ZeroOrMore(Group(leaseStatement))) + RBRACE

        with open(self.lease_file, 'r') as file:
            parsed = leaseDef.scanString(file.read())

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

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return self.list.keys()

    def __getitem__(self, item):
        return self.list[item]

    def __contains__(self, item):
        return item in self.list

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return repr(self.list)
