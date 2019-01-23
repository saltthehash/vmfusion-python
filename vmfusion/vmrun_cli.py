import os
import subprocess
from typing import Optional, List, Dict

from .exceptions import VMRunException
from .utils import get_abspath, file_must_exist


class VMRunCLI(object):
    """Human readable python interface to the vmrun cli tool of VMware Fusion.

    Tested with VMware Fusion 5."""

    def __init__(self, bundle_directory: Optional[str] = None, vmrun_path: Optional[str] = None):
        if not vmrun_path:
            if not bundle_directory:
                bundle_directory: str = '/Applications/VMware Fusion.app'

            vmrun_full_path: str = os.path.join(bundle_directory, 'Contents/Library/vmrun')
        else:
            vmrun_full_path: str = vmrun_path

        if not os.path.isfile(vmrun_full_path):
            raise ValueError("vmrun tool not found at path {0}".format(vmrun_full_path))

        self.tool_path: str = vmrun_full_path

    def __vmrun(self, command: List[str]):
        base = [self.tool_path, '-T', 'fusion']
        base.extend(command)

        proc = subprocess.Popen(base, stdout=subprocess.PIPE)
        stdout = proc.stdout.readlines()

        if len(stdout) and stdout[0].startswith(b'Error'):
            raise VMRunException(stdout[0])

        return stdout

    def list(self) -> Dict:
        output = self.__vmrun(['list'])

        # Expected output:
        # Total running VMs: N
        # [optional absolute path to VMX 1]
        # [optional absolute path to VMX 2]
        # [optional absolute path to VMX n]
        return {'count': int(output[0].split(b':')[1].strip()),
                'machines': [vmx.strip() for vmx in output[1:]]}

    def start(self, vmx: str, gui: bool = True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        gui_value = 'gui' if gui else 'nogui'
        self.__vmrun(['start', vmx, gui_value])

    def stop(self, vmx: str, soft: bool = True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['stop', vmx, soft_value])

    def reset(self, vmx: str, soft: bool = True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['reset', vmx, soft_value])

    def suspend(self, vmx: str, soft: bool = True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['suspend', vmx, soft_value])

    def pause(self, vmx: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['pause', vmx])

    def unpause(self, vmx: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['unpause', vmx])

    def delete(self, vmx: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['delete', vmx])

    def list_snapshots(self, vmx: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        output = self.__vmrun(['listSnapshots', vmx])
        snapshots = [s.strip() for s in output[1:]]
        data = {'count': len(snapshots), 'snapshots': snapshots}

        return data

    def snapshot(self, vmx: str, name: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['snapshot', vmx, name])

    def revert_to_snapshot(self, vmx: str, name: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['revertToSnapshot', vmx, name])

    def delete_snapshot(self, vmx: str, name: str):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['deleteSnapshot', vmx, name])


# Default access
vmrun = VMRunCLI()
