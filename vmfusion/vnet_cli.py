import re
from typing import Optional

from .dhcpd_leases import DHCPDLeases


class VNetCLI(object):
    def __init__(self, name: str):
        self.name: str = name
        self.leases: Optional[DHCPDLeases] = None
        self.dhcp: bool = False
        self.netmask: Optional[str] = None
        self.subnet: Optional[str] = None
        self.nat: bool = False
        self.virtual_adapter: bool = False

        self._parse_networking()
        self._load_dhcp_leases()

    def _load_dhcp_leases(self):
        try:
            path: str = '/var/db/vmware/vmnet-dhcpd-{}.leases'
            self.leases = DHCPDLeases(path.format(self.name))
            self.leases.load()
        except ValueError:
            pass

    def _parse_networking(self):
        netfile = "/Library/Preferences/VMware Fusion/networking"
        net_num = self.name[-1]
        net_name = "VNET_{0}".format(net_num)
        match = re.compile(r"answer\s+{0}_(\w+)\s+(.*)$".format(net_name)).match
        attrs = {}

        with open(netfile) as net:
            content = net.read()
            if net_name not in content:
                msg = "No network named {0} is defined!"
                raise ValueError(msg.format(self.name))

            for line in content.split("\n"):
                m = match(line)
                if m:
                    attr = m.group(1).lower()
                    val = m.group(2)
                    if val == 'yes':
                        val = True
                    elif val == 'no':
                        val = False
                    attrs[attr] = val

        self.dhcp = attrs.get("dhcp", False)
        self.netmask = attrs.get("hostonly_netmask", None)
        self.subnet = attrs.get("hostonly_subnet", None)
        self.nat = attrs.get("nat", False)
        self.virtual_adapter = attrs.get("virtual_adapter", False)


# Default access
vmnet_hostonly: VNetCLI = VNetCLI('vmnet1')
vmnet_nat: VNetCLI = VNetCLI('vmnet8')
