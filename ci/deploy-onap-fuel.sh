#!/bin/bash
#
# Copyright 2018 Tieto
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script for automated deployment of ONAP on top of OPNFV Fuel/MCP installation
# In the future both OOM and heat install methods should be supported.
# At the beginning OOM will be used for simplification.

# TODO:
#   Configure ONAP to be able to control underlying OpenStack
#   Implement support for ONAP configuration, i.e. ONAP component selection
#   for installation

# configuration to be passed to ci/deploy-onap.sh
export SSH_USER="ubuntu"
export SSH_IDENTITY="/root/auto_key.pem"

# configuration
AUTO_INSTALL_DIR=${AUTO_INSTALL_DIR:-"."}

echo -e "\nOpenStack configuration\n"

# Download VM images and import them
mkdir /opt/images
wget -P /opt/images https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img
glance image-create --name 'xenial' --disk-format=qcow2 --container-format=bare --visibility=public --file /opt/images/xenial-server-cloudimg-amd64-disk1.img

# Create xlarge flavor
openstack flavor create --ram 64000  --vcpus 16 --disk 45 m1.xlarge
# Generate a keypair and store private key
openstack keypair create auto_keys > $SSH_IDENTITY
chmod 600 $SSH_IDENTITY

# Modify quotas
openstack quota set --ram 128000 admin
openstack quota set --cores 32 admin

# Configure networking with DNS for access to the internet
openstack network create onap_private_network --provider-network-type vxlan
openstack subnet create onap_private_subnet --network onap_private_network --subnet-range 192.168.33.0/24 --ip-version 4 --dhcp --dns-nameserver "8.8.8.8"
openstack router create onap_router
openstack router add subnet onap_router onap_private_subnet
openstack router set onap_router --external-gateway floating_net

# Allow ICMP, SSH, 443, 80 and 8080 protocols and ports to VMs
openstack security group create onap_security_group
openstack security group rule create --protocol icmp onap_security_group
openstack security group rule create  --proto tcp --dst-port 22:22 onap_security_group
openstack security group rule create  --proto tcp --dst-port 8080:8080 onap_security_group
openstack security group rule create  --proto tcp --dst-port 80:80 onap_security_group
openstack security group rule create  --proto tcp --dst-port 443:443 onap_security_group
# Allow communication between k8s cluster nodes
PUBLIC_NET=`openstack subnet list --name floating_subnet -f value -c Subnet`
openstack security group rule create --remote-ip $PUBLIC_NET --proto tcp --dst-port 1:65535 onap_security_group
openstack security group rule create --remote-ip $PUBLIC_NET --proto udp --dst-port 1:65535 onap_security_group


# Create 2 VMs and assign floating IPs to them
openstack floating ip create floating_net
VM1_IP=`openstack floating ip list --port "" -c "Floating IP Address" -f value`
openstack server create --flavor m1.xlarge --image xenial --nic net-id=onap_private_network --security-group onap_security_group --key-name auto_keys vm1
sleep 5 # wait for VM init before floating IP can be assigned
openstack server add floating ip vm1 $VM1_IP
openstack floating ip create floating_net
VM2_IP=`openstack floating ip list -c "Floating IP Address" -c "Port" -f value | grep None | cut -f1 -d " "`
openstack server create --flavor m1.xlarge --image xenial --nic net-id=onap_private_network --security-group onap_security_group --key-name auto_keys vm2
sleep 5 # wait for VM init before floating IP can be assigned
openstack server add floating ip vm2 $VM2_IP

openstack server list

echo "Waiting for 5 minutes at $(date)"
sleep 5m # wait until VMs will be up & running

DATE_START=$(date)
echo -e "\nONAP Installation Started at $DATE_START\n"
$AUTO_INSTALL_DIR/ci/deploy-onap.sh $VM1_IP $VM2_IP
echo -e "\nONAP Installation Started at $DATE_START"
echo -e "ONAP Installation Finished at $(date)\n"
