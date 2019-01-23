import os
import subprocess

from .utils import file_must_not_exist, file_must_exist


class VDiskManagerCLI(object):
    # Valid disks
    SPARSE_SINGLE = 'SPARSE_SINGLE'
    SPARSE_SPLIT = 'SPARSE_SPLIT'
    PREALLOC_SINGLE = 'PREALLOC_SINGLE'
    PREALLOC_SPLIT = 'PREALLOC_SPLIT'
    disk_type_map = {
        'SPARSE_SINGLE': '0',
        'SPARSE_SPLIT': '1',
        'PREALLOC_SINGLE': '2',
        'PREALLOC_SPLIT': '3'
    }

    # Valid adapters
    IDE = 'ide'
    LSILOGIC = 'lsilogic'
    BUSLOGIC = 'buslogic'
    adapters = [IDE, LSILOGIC, BUSLOGIC]

    """Human readable python interface to the vmware-vdiskmanager cli of VMware Fusion.

    Tested with VMware Fusion 5."""

    def __init__(self, bundle_directory=None):
        if not bundle_directory:
            bundle_directory = '/Applications/VMware Fusion.app'

        vmrun = os.path.join(bundle_directory, 'Contents/Library/vmware-vdiskmanager')

        if not os.path.isfile(vmrun):
            raise ValueError("vmrun tool not found at path {0}".format(vmrun))

        self.tool_path = vmrun

    def __vdiskmanager(self, command):
        base = [self.tool_path]
        base.extend(command)

        proc = subprocess.call(base)

    def create(self, vmdk, size, disk_type=None, adapter_type=None):
        file_must_not_exist('VMDK', vmdk)

        # disk type
        if not disk_type:
            disk_type = self.SPARSE_SPLIT

        if disk_type not in self.disk_type_map:
            raise ValueError("Invalid disk type {0}".format(disk_type))

        # adapter type
        if not adapter_type:
            adapter_type = self.LSILOGIC

        if adapter_type not in self.adapters:
            raise ValueError("Invalid adapter type {0}".format(adapter_type))

        self.__vdiskmanager(['-c', '-s', size, '-a', adapter_type, '-t', self.disk_type_map[disk_type], vmdk])

    def defragment(self, vmdk):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-d', vmdk])

    def shrink(self, vmdk):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-k', vmdk])

    def rename(self, source_vmdk, destination_vmdk):
        file_must_exist('VMDK', source_vmdk)
        file_must_not_exist('VMDK', destination_vmdk)

        self.__vdiskmanager(['-n', source_vmdk, destination_vmdk])

    def convert(self, vmdk, disk_type):
        file_must_exist('VMDK', vmdk)

        if disk_type not in self.disk_type_map:
            raise ValueError("Invalid disk type {0}".format(disk_type))

        self.__vdiskmanager(['-r', '-t', self.disk_type_map[disk_type], vmdk])

    def expand(self, vmdk, new_size):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-x', new_size, vmdk])


# Default access
vdiskmanager = VDiskManagerCLI()
