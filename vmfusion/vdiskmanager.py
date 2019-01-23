import os
import subprocess
from typing import Optional, Dict, List

from .utils import file_must_not_exist, file_must_exist


class VDiskManagerCLI:
    # Valid disks
    SPARSE_SINGLE: str = 'SPARSE_SINGLE'
    SPARSE_SPLIT: str = 'SPARSE_SPLIT'
    PREALLOC_SINGLE: str = 'PREALLOC_SINGLE'
    PREALLOC_SPLIT: str = 'PREALLOC_SPLIT'
    disk_type_map: Dict[str, str] = {
        'SPARSE_SINGLE': '0',
        'SPARSE_SPLIT': '1',
        'PREALLOC_SINGLE': '2',
        'PREALLOC_SPLIT': '3'
    }

    # Valid adapters
    IDE: str = 'ide'
    LSILOGIC: str = 'lsilogic'
    BUSLOGIC: str = 'buslogic'
    adapters: List[str] = [IDE, LSILOGIC, BUSLOGIC]

    """Human readable python interface to the vmware-vdiskmanager cli of VMware Fusion.

    Tested with VMware Fusion 5."""

    def __init__(self, bundle_directory: Optional[str] = None):
        if not bundle_directory:
            bundle_directory: str = '/Applications/VMware Fusion.app'

        vdiskmanager_path: str = os.path.join(bundle_directory, 'Contents/Library/vmware-vdiskmanager')

        if not os.path.isfile(vdiskmanager_path):
            raise ValueError("vmrun tool not found at path {0}".format(vdiskmanager_path))

        self.tool_path: str = vdiskmanager_path

    def __vdiskmanager(self, command: List[str]):
        base: List[str] = [self.tool_path]
        base.extend(command)

        subprocess.call(base)

    def create(self, vmdk: str, size: int, disk_type: Optional[str] = None, adapter_type: Optional[str] = None):
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

        self.__vdiskmanager(['-c', '-s', str(size), '-a', adapter_type, '-t', self.disk_type_map[disk_type], vmdk])

    def defragment(self, vmdk: str):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-d', vmdk])

    def shrink(self, vmdk: str):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-k', vmdk])

    def rename(self, source_vmdk: str, destination_vmdk: str):
        file_must_exist('VMDK', source_vmdk)
        file_must_not_exist('VMDK', destination_vmdk)

        self.__vdiskmanager(['-n', source_vmdk, destination_vmdk])

    def convert(self, vmdk: str, disk_type: str):
        file_must_exist('VMDK', vmdk)

        if disk_type not in self.disk_type_map:
            raise ValueError("Invalid disk type {0}".format(disk_type))

        self.__vdiskmanager(['-r', '-t', self.disk_type_map[disk_type], vmdk])

    def expand(self, vmdk: str, new_size: int):
        file_must_exist('VMDK', vmdk)

        self.__vdiskmanager(['-x', str(new_size), vmdk])


# Default access
vdiskmanager = VDiskManagerCLI()
