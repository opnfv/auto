#!/usr/bin/env bash

# /usr/bin/env bash or /bin/bash ? /usr/bin/env bash is more environment-independent
# beware of files which were edited in Windows, and have invisible \r end-of-line characters, causing Linux errors

##############################################################################
# Copyright (c) 2018 Wipro Limited and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# OPNFV contribution guidelines Wiki page:
# https://wiki.opnfv.org/display/DEV/Contribution+Guidelines

# OPNFV/Auto project:
# https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095


# localization control: force script to use default language for output, and force sorting to be bytewise
# ("C" is from C language, represents "safe" locale everywhere)
# (result: the script will consider only basic ASCII characters and disable UTF-8 multibyte match)
export LANG=C
export LC_ALL=C

##############################################################################
## installation of OpenStack via OPNFV Fuel/MCP, on Ubuntu, virtual deployment
##############################################################################
# reference manual: https://docs.opnfv.org/en/latest/submodules/fuel/docs/release/installation/index.html
# page for virtual deployment: https://docs.opnfv.org/en/latest/submodules/fuel/docs/release/installation/installation.instruction.html#opnfv-software-installation-and-deployment

# Steps:
# step 1: download Fuel/MCP repository and run deploy script
#    (this example: x86, virtual deploy, os-nosdn-nofeature-noha scenario)
# step 2: download additional packages (python3, OpenStackSDK, OpenStack clients, ...)
# step 3: add more resources to OpenStack instance (vCPUs, RAM)
# step 4: download Auto repository
# step 5: run Auto python script to populate OpenStack instance with objects expected by ONAP


echo "*** begin AUTO install: OPNFV Fuel/MCP"


# step 1: download Fuel/MCP repository and run deploy script

#   prepare install directory
export INSTALLDIR=/opt/opnfv-fuel
mkdir -p $INSTALLDIR
cd $INSTALLDIR

#   get Fuel repository
git clone https://git.opnfv.org/fuel
#   cd in new fuel repository, which contains directories: mcp, ci, etc.
#   note: this is for x86_64 architectures; for aarch64 architectures, git clone https://git.opnfv.org/armband and cd armband instead
cd fuel

#   edit NOHA scenario YAML file with more resources for compute nodes: 32 vCPUs, 192G RAM
echo "  cmp01:"        >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml
echo "    vcpus: 32"   >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml
echo "    ram: 196608" >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml
echo "  cmp02:"        >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml
echo "    vcpus: 32"   >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml
echo "    ram: 196608" >> mcp/config/scenario/os-nosdn-nofeature-noha.yaml

#   provide more storage space to VMs: 350G per compute node (default is 100G)
sed -i mcp/scripts/lib.sh -e 's/\(qemu-img create.*\) 100G/\1 350G/g'

#   launch OPNFV Fuel/MCP deploy script
ci/deploy.sh -l local -p virtual1 -s os-nosdn-nofeature-noha -D |& tee deploy.log



# step 2: download additional packages (python3, OpenStackSDK, OpenStack clients, ...)

# install python 3 on Ubuntu
echo "*** begin install python 3"
sudo apt-get -y update
sudo apt-get -y install python3
# maybe clean-up packages
# sudo apt -y autoremove
# specific install of a python version, e.g. 3.6
# sudo apt-get install python3.6

# http://docs.python-guide.org/en/latest/starting/install3/linux/
# sudo apt-get install software-properties-common
# sudo add-apt-repository ppa:deadsnakes/ppa
# sudo apt-get update
# sudo apt-get install python3.6
echo "python2 --version: $(python2 --version)"
echo "python3 --version: $(python3 --version)"
echo "which python: $(which python)"

# install pip3 for python3; /usr/local/bin/pip3 vs. /usr/bin/pip3; solve with "hash -r"
echo "*** begin install pip3 for python3"
apt -y install python3-pip
hash -r
pip3 install --upgrade pip
hash -r

echo "\$PATH:" $PATH
echo "which pip: $(which pip)"
echo "which pip3: $(which pip3)"

# install OpenStack SDK Python client
echo "*** begin install OpenStack SDK Python client"
pip3 install openstacksdk
pip3 install --upgrade openstacksdk

# install OpenStack CLI
echo "*** begin install OpenStack CLI"
pip3 install python-openstackclient
pip3 install --upgrade python-openstackclient

pip3 install --upgrade python-keystoneclient
pip3 install --upgrade python-neutronclient
pip3 install --upgrade python-novaclient
pip3 install --upgrade python-glanceclient
pip3 install --upgrade python-cinderclient

# install OpenStack Heat (may not be installed by default), may be useful for VNF installation
#apt install python3-heatclient
echo "*** begin install OpenStack Heat"
pip3 install --upgrade python-heatclient

# package verification printouts
echo "*** begin package verification printouts"
pip3 list
pip3 show openstacksdk
pip3 check



# step 3: add more resources to OpenStack instance

# now that OpenStack CLI is installed, finish Fuel/MCP installation:
# take extra resources indicated in os-nosdn-nofeature-noha.yaml into account as quotas in the OpenStack instance
# (e.g. 2 compute nodes with 32 vCPUs and 192G RAM each => 64 cores and 384G=393,216M RAM)
# enter environment variables hard-coded here, since always the same for Fuel/MCP; there could be better ways to do this :)

export OS_AUTH_URL=http://10.16.0.107:5000/v3
export OS_PROJECT_NAME="admin"
export OS_USER_DOMAIN_NAME="Default"
export OS_PROJECT_DOMAIN_ID="default"
unset OS_TENANT_ID
unset OS_TENANT_NAME
export OS_USERNAME="admin"
export OS_PASSWORD="opnfv_secret"
export OS_REGION_NAME="RegionOne"
export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=3

# at this point, openstack CLI commands should work
echo "*** finish install OPNFV Fuel/MCP"
openstack quota set --cores 64 admin
openstack quota set --ram 393216 admin



# step 4: download Auto repository

# install OPNFV Auto
#   prepare install directory
echo "*** begin install OPNFV Auto"
mkdir -p /opt/opnfv-Auto
cd /opt/opnfv-Auto
#   get Auto repository from Gerrit
git clone https://gerrit.opnfv.org/gerrit/auto
#   cd in new auto repository, which contains directories: lib, setup, ci, etc.
cd auto



# step 5: run Auto python script to populate OpenStack instance with objects expected by ONAP

# download images used by script, unless downloading images from URL works from the script
echo "*** begin download images"
cd setup/VIMs/OpenStack
mkdir images
cd images
#CirrOS
curl -O http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
curl -O http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-arm-disk.img
curl -O http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-aarch64-disk.img
# Ubuntu 16.04 LTS (Xenial Xerus)
curl -O https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img
curl -O https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-arm64-disk1.img
# Ubuntu 14.04.5 LTS (Trusty Tahr)
curl -O http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
curl -O http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-arm64-disk1.img

# launch script to populate the OpenStack instance
echo "*** begin populate OpenStack instance with ONAP objects"
cd ..
python3 auto_script_config_openstack_for_onap.py

echo "*** end AUTO install: OPNFV Fuel/MCP"

