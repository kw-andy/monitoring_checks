import unittest
from unittest.mock import patch, Mock

from migfailoverip import get_vm_failover_ip
from migfailoverip import get_vm_mac_address
from migfailoverip import get_host_ip
from migfailoverip import is_failover_ip_associated_to_mac_address
from migfailoverip import update_failover_ip


RAW_PVE_VM_CONFIG_EXAMPLE = """boot: c
bootdisk: scsi0
ciuser: mlf
cores: 4
hookscript: cephfs:snippets/migfailoverip.py
ide2: ceph-rbd:vm-178-cloudinit,media=cdrom
ipconfig0: ip=195.154.42.185/32,gw=62.210.0.1
ipconfig1: ip=192.168.22.42/24
memory: 4096
name: ppd-bbb-2
nameserver: 62.210.16.6 62.210.16.7
net0: virtio=52:54:00:00:c7:fd,bridge=vmbr0
net1: virtio=A6:64:49:04:7D:CD,bridge=vmbr3
numa: 0
onboot: 1
ostype: l26
parent: clean
scsi0: ceph-rbd:base-1004-disk-0/vm-178-disk-0,size=256204M
scsihw: virtio-scsi-pci
serial0: socket
smbios1: uuid=f21e8abc-5763-438c-9a40-41504953ffad
sockets: 1
vga: serial0
vmgenid: d57de0ba-0ec8-48a9-a8ac-465cbcf95dee"""

RAW_HOST_IP_SHOW = 'vmbr0            UP             195.154.27.54/24 \n'


def mock_get_raw_pve_vm_config(vmid):
    return RAW_PVE_VM_CONFIG_EXAMPLE


class TestMigFailoverIP(unittest.TestCase):
 
    @patch(
        'migfailoverip.get_raw_pve_vm_config',
        return_value=RAW_PVE_VM_CONFIG_EXAMPLE
    )
    def test_get_vm_failover_ip(self, get_vm_failover_ip_func):
        public_ip = get_vm_failover_ip('178')
        self.assertEqual(public_ip, '195.154.42.185')
 
    @patch(
        'migfailoverip.get_raw_pve_vm_config',
        return_value=RAW_PVE_VM_CONFIG_EXAMPLE
    )
    def test_get_vm_mac_address(self, get_vm_mac_address_func):
        mac_address = get_vm_mac_address('178')
        self.assertEqual(mac_address, '52:54:00:00:c7:fd')


    @patch('failoverproviders.OnlineFailoverProvider.is_failover_associated_to_mac',
        return_value=True
        )
    def test_is_failover_ip_associated_to_mac_address(
        self,
        mock_failover_provider,
        ):
        self.assertTrue(is_failover_ip_associated_to_mac_address(
            '195.154.42.185', '52:54:00:00:c7:fd'))

    @patch('failoverproviders.OnlineFailoverProvider.update_failover_destination',
        return_value=True
        )
    def test_update_failover_ip(
        self,
        mock_failover_provider,
        ):
        self.assertEqual(update_failover_ip(
            '195.154.42.185', '195.154.27.54'), True)


if __name__ == '__main__':
    unittest.main()
