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

#
# functions
#
# function minimum accepts two numbers and prints smaller one
function minimum(){
    echo $(($1<$2?$1:$2))

}

# configuration to be passed to ci/deploy-onap.sh
export SSH_USER="ubuntu"
export SSH_IDENTITY="/root/onap_key.pem"

# use default values if compute configuration was not set by FUEL installer (or user)
AUTO_INSTALL_DIR=${AUTO_INSTALL_DIR:-"."}
CMP_COUNT=${CMP_COUNT:-2}                       # number of compute nodes
CMP_MIN_MEM=${CMP_MIN_MEM:-64000}               # MB RAM of the weakest compute node
CMP_MIN_CPUS=${CMP_MIN_CPUS:-32}                # CPU count of the weakest compute node
CMP_STORAGE_TOTAL=${CMP_STORAGE_TOTAL:-$((70*$CMP_COUNT))} # size of storage for instances
VM_COUNT=${VM_COUNT:-$CMP_COUNT}                # number of VMs to be created for k8s cluster

echo -e "\nOpenStack configuration"

# calculate VM resources, so that flavor can be created
echo "Configuraiton of compute node:"
echo "Number of nodes:       CMP_COUNT=$CMP_COUNT"
echo "Minimal RAM:           CMP_MIN_MEM=$CMP_MIN_MEM"
echo "Minimal CPUs count:    CMP_MIN_CPUS=$CMP_MIN_CPUS"
echo "Storage for instances: CMP_STORAGE_TOTAL=$CMP_STORAGE_TOTAL"
# calculate VM parameters; there will be up to 1 VM per Compute node
# to maximize resources available for VMs
PER=85                      # % of compute resources will be consumed by VM
VM_DISK_MAX=100             # GB - max VM disk size in case that storage is huge
VM_MEM_MAX=80000            # MB - max VM RAM size in case that compute RAM is huge
VM_CPUS_MAX=42              # max count of VM CPUs in case that compute has planty of cores
VM_MEM=$(minimum $(($CMP_MIN_MEM*$PER/100)) $VM_MEM_MAX)
VM_CPUS=$(minimum $(($CMP_MIN_CPUS*$PER/100)) $VM_CPUS_MAX)
VM_DISK=$(minimum $(($CMP_STORAGE_TOTAL*$PER/100/$CMP_COUNT)) $VM_DISK_MAX)

echo "Flavor configuration:"
echo "CPUs      : $VM_CPUS"
echo "RAM [MB]  : $VM_MEM"
echo "DISK [GB] : $VM_DISK"

# Create onap flavor
openstack flavor create --ram $VM_MEM  --vcpus $VM_CPUS --disk $VM_DISK onap.large

# Generate a keypair and store private key
openstack keypair create onap_key > $SSH_IDENTITY
chmod 600 $SSH_IDENTITY

# Download VM images and import them
mkdir /opt/images
wget -P /opt/images https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img
openstack image create --disk-format qcow2 --container-format bare --public --file /opt/images/xenial-server-cloudimg-amd64-disk1.img xenial

# Modify quotas
openstack quota set --ram $(($VM_MEM*$VM_COUNT)) admin
openstack quota set --cores $(($VM_CPUS*$VM_COUNT)) admin

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
openstack security group rule create  --proto tcp --dst-port 8080:8080 onap_security_group # rancher
openstack security group rule create  --proto tcp --dst-port 8078:8078 onap_security_group # horizon
openstack security group rule create  --proto tcp --dst-port 8879:8879 onap_security_group # helm
openstack security group rule create  --proto tcp --dst-port 80:80 onap_security_group
openstack security group rule create  --proto tcp --dst-port 443:443 onap_security_group
# Allow communication between k8s cluster nodes
PUBLIC_NET=`openstack subnet list --name floating_subnet -f value -c Subnet`
openstack security group rule create --remote-ip $PUBLIC_NET --proto tcp --dst-port 1:65535 onap_security_group
openstack security group rule create --remote-ip $PUBLIC_NET --proto udp --dst-port 1:65535 onap_security_group

# Create 2 VMs and assign floating IPs to them
VM_ITER=1
while [ $VM_ITER -le $VM_COUNT ] ; do
    openstack floating ip create floating_net
    VM_NAME[$VM_ITER]="onap_vm${VM_ITER}"
    VM_IP[$VM_ITER]=$(openstack floating ip list -c "Floating IP Address" -c "Port" -f value | grep None | cut -f1 -d " " | head -n1)
    openstack server create --flavor onap.large --image xenial --nic net-id=onap_private_network --security-group onap_security_group --key-name onap_key ${VM_NAME[$VM_ITER]}
    sleep 5 # wait for VM init before floating IP can be assigned
    openstack server add floating ip ${VM_NAME[$VM_ITER]} ${VM_IP[$VM_ITER]}
    VM_ITER=$(($VM_ITER+1))
done

openstack server list

echo "Waiting for VMs to start up for 5 minutes at $(date)"
sleep 5m # wait until VMs will be up & running

openstack server list

DATE_START=$(date)
echo -e "\nONAP Installation Started at $DATE_START\n"

$AUTO_INSTALL_DIR/ci/deploy-onap.sh ${VM_IP[@]}

echo -e "\nONAP Installation Started at $DATE_START"
echo -e "ONAP Installation Finished at $(date)\n"
