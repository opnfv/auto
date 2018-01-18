"""ONAP stack parameters"""

ONAP_PROJECT_NAME = "onap"

ONAP_VM_IMAGES = {
        "ubuntu_1404_image": {
            "name": "Ubuntu_14.04_trusty",
            "url": "https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img"
        },
        "ubuntu_1604_image": {
            "name": "Ubuntu_16.04_xenial",
            "url": "https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img"
        },
        "centos_7_image": {
            "name": "Centos_7",
            "url": "https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-1711.qcow2"
        }
    }

ONAP_SECURITY_RULES = [
        {
            "protocol": "tcp",
            "direction": "ingress",
            "port_range_min": 1,
            "port_range_max": 65535
        }
    ]

ONAP_QUOTA = {"instances": 100, "cores": 100, "ram": 204800}

ONAP_KEYPAIR = {
        "name": "onap_key",
        "prikey_path": "~/.ssh/id_rsa",
        "pubkey_path": "~/.ssh/id_rsa.pub"
    }

ONAP_STACK_CONFIG = {
    "public_net_name": "ext-net"
    "ubuntu_1404_image": ONAP_VM_IMAGES['ubuntu_1404_image']['name']
    "ubuntu_1604_image": ONAP_VM_IMAGES['ubuntu_1604_image']['name']
    "flavor_small": "m1.small"
    "flavor_medium": "m1.medium"
    "flavor_large": "m1.large"
    "flavor_xlarge": "m1.xlarge"
    "flavor_xxlarge": "m1.xlarge"
    "vm_base_name": "onap"
    "key_name": ONAP_KEYPAIR['name']
    "pub_key": ONAP_KEYPAIR['pubkey_path']
    "nexus_repo": "https://nexus.onap.org/content/sites/raw"
    "nexus_docker_repo": "nexus3.onap.org:10001"
    "nexus_username": "docker"
    "nexus_password": "docker"
    "dmaap_topic": "AUTO"
    "artifacts_version": "1.1.1"
    "openstack_tenant_name": "admin"
    "openstack_username": "admin"
    "openstack_api_key": "49ef27251b38c5124378010e7be8758eb"
    "openstack_auth_method": "password"
    "openstack_region": "RegionOne"
    "horizon_url": "https://192.168.22.222:80"
    "keystone_url": "https://192.168.22.222:5000"
    "cloud_env": "openstack"
    }
