from .utils import get_abspath, file_must_exist
from .vmrun_cli import VMRunCLI


class VM(object):
    """
    A virtual machine.
    """

    def __init__(self, vmx):
        self.vmx = get_abspath(vmx)
        file_must_exist('VMX', self.vmx)
        self.vmrun = VMRunCLI()

    def start(self, gui=True):
        return self.vmrun.start(self.vmx, gui)

    def stop(self, soft=True):
        return self.vmrun.stop(self.vmx, soft)

    def reset(self, soft=True):
        return self.vmrun.reset(self.vmx, soft)

    def suspend(self, soft=True):
        return self.vmrun.suspend(self.vmx, soft)

    def pause(self):
        return self.vmrun.pause(self.vmx)

    def unpause(self):
        return self.vmrun.unpause(self.vmx)

    def delete(self):
        return self.vmrun.delete(self.vmx)

    def list_snapshots(self):
        return self.vmrun.list_snapshots(self.vmx)

    def snapshot(self, name):
        return self.vmrun.snapshot(self.vmx, name)

    def revert_to_snapshot(self, name):
        return self.vmrun.revert_to_snapshot(self.vmx, name)

    def delete_snapshot(self, name):
        return self.vmrun.delete_snapshot(self.vmx, name)
