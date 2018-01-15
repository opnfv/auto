"""ONAP stack parameters"""

ONAP_TENANT_NAME = "onapx"
ONAP_VM_IMAGES = {
        "Ubuntu_14.04_trusty": "https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img",
        "Ubuntu_16.04_xenial": "https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img",
        "Centos_7": "https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1711.qcow2"
    }
ONAP_SECURITY_RULE = {
        "protocol": "tcp",
        "direction": "ingress",
        "port_range_min": 1,
        "port_range_max": 65535
    }
