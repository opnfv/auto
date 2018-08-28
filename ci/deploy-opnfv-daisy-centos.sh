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


###############################################################################
## installation of OpenStack via OPNFV Daisy4nfv, on CentOS, virtual deployment
###############################################################################
# reference manual: https://docs.opnfv.org/en/stable-fraser/submodules/daisy/docs/release/installation/index.html#daisy-installation
# page for virtual deployment: https://docs.opnfv.org/en/stable-fraser/submodules/daisy/docs/release/installation/vmdeploy.html

echo "*** begin AUTO install: OPNFV Daisy4nfv"

# check OS version
echo "*** print OS version (must be CentOS, version 7.2 or more)"
cat /etc/*release

# make sure cp is not aliased or a function; same for mv and rm
unalias cp
unset -f cp
unalias mv
unset -f mv
unalias rm
unset -f rm

# Manage Nested Virtualization
echo "*** ensure Nested Virtualization is enabled on Intel x86"
echo "***   nested flag before:"
cat /sys/module/kvm_intel/parameters/nested
rm -f /etc/modprobe.d/kvm-nested.conf
{ printf "options kvm-intel nested=1\n";\
  printf "options kvm-intel enable_shadow_vmcs=1\n";\
  printf "options kvm-intel enable_apicv=1\n";\
  printf "options kvm-intel ept=1\n"; } >> /etc/modprobe.d/kvm-nested.conf
sudo modprobe -r kvm_intel
sudo modprobe -a kvm_intel
echo "***   nested flag after:"
cat /sys/module/kvm_intel/parameters/nested

echo "*** verify status of modules in the Linux Kernel: kvm_intel module should be loaded for x86_64 machines"
lsmod | grep kvm_
grep kvm_ < /proc/modules

# download tools: git, kvm, libvirt, python-yaml
sudo yum -y install git
sudo yum -y install kvm
sudo yum -y install libvirt
sudo yum info libvirt
sudo yum info qemu-kvm
sudo yum -y install python-yaml


# make sure SELinux is enforced (Security-Enhanced Linux)
sudo setenforce 1
echo "getenforce: $(getenforce)"

# Restart the libvirtd daemon:
sudo service libvirtd restart
# Verify if the kvm module is loaded, you should see amd or intel depending on the hardware:
lsmod | grep kvm
# Note: to test, issue a virsh command to ensure local root connectivity:
# sudo virsh sysinfo



# update everything (upgrade: riskier than update, as packages supposed to be unused will be deleted)
# (note: can take several minutes; may not be necessary)
sudo yum -y update

# prepare Daisy installation directory
export INSTALLDIR=/opt/opnfv-daisy
mkdir $INSTALLDIR
cd $INSTALLDIR

# oslo-config, needed in daisy/deploy/get_conf.py
sudo curl -O https://bootstrap.pypa.io/get-pip.py
hash -r
python get-pip.py --no-warn-script-location
pip install --upgrade oslo-config


# retrieve Daisy4nfv repository
git clone https://gerrit.opnfv.org/gerrit/daisy
cd daisy



# OPTION 1: master repo and latest bin file: May 17th 2018
# Download latest bin file from http://artifacts.opnfv.org/daisy.html and name it opnfv.bin
curl http://artifacts.opnfv.org/daisy/opnfv-2018-05-17_14-00-32.bin -o opnfv.bin
# make opnfv.bin executable
chmod 777 opnfv.bin

# OPTION 2: stable release: Fraser 6.0 (so, checkout to stable Fraser release opnfv-6.0)
# Download matching bin file from http://artifacts.opnfv.org/daisy.html and name it opnfv.bin
#git checkout opnfv.6.0 # as per Daisy4nfv instructions, but does not work
#git checkout stable/fraser
#curl http://artifacts.opnfv.org/daisy/fraser/opnfv-6.0.iso -o opnfv.bin
# make opnfv.bin executable
#chmod 777 opnfv.bin



# The deploy.yaml file is the inventory template of deployment nodes:
# error from doc: ”./deploy/conf/vm_environment/zte-virtual1/deploy.yml”
# correct path:   "./deploy/config/vm_environment/zte-virtual1/deploy.yml”
# You can write your own name/roles reference into it:
#   name – Host name for deployment node after installation.
#   roles – Components deployed.
# note: ./templates/virtual_environment/ contains xml files, for networks and VMs


# prepare config dir for Auto lab in daisy dir, and copy deploy and network YAML files from default files (virtual1 or virtual2)
export AUTO_DAISY_LAB_CONFIG1=labs/auto_daisy_lab/virtual1/daisy/config
export DAISY_DEFAULT_ENV1=deploy/config/vm_environment/zte-virtual1
mkdir -p $AUTO_DAISY_LAB_CONFIG1
cp $DAISY_DEFAULT_ENV1/deploy.yml $AUTO_DAISY_LAB_CONFIG1
cp $DAISY_DEFAULT_ENV1/network.yml $AUTO_DAISY_LAB_CONFIG1

export AUTO_DAISY_LAB_CONFIG2=labs/auto_daisy_lab/virtual2/daisy/config
export DAISY_DEFAULT_ENV2=deploy/config/vm_environment/zte-virtual2
mkdir -p $AUTO_DAISY_LAB_CONFIG2
cp $DAISY_DEFAULT_ENV2/deploy.yml $AUTO_DAISY_LAB_CONFIG2
cp $DAISY_DEFAULT_ENV2/network.yml $AUTO_DAISY_LAB_CONFIG2

# Note:
# - zte-virtual1 config files deploy openstack with five nodes (3 LB nodes and 2 computer nodes).
# - zte-virtual2 config files deploy an all-in-one openstack

# run deploy script, scenario os-nosdn-nofeature-ha, multinode OpenStack
sudo ./ci/deploy/deploy.sh -L "$(cd ./;pwd)" -l auto_daisy_lab -p virtual1 -s os-nosdn-nofeature-ha

# run deploy script, scenario os-nosdn-nofeature-noha, all-in-one OpenStack
# sudo ./ci/deploy/deploy.sh -L "$(cd ./;pwd)" -l auto_daisy_lab -p virtual2 -s os-nosdn-nofeature-noha


# Notes about deploy.sh:
# The value after -L should be an absolute path which points to the directory which includes $AUTO_DAISY_LAB_CONFIG directory.
# The value after -p parameter (virtual1 or virtual2) should match the one selected for $AUTO_DAISY_LAB_CONFIG.
# The value after -l parameter (e.g. auto_daisy_lab) should match the lab name selected for $AUTO_DAISY_LAB_CONFIG, after labs/ .
# Scenario (-s parameter): “os-nosdn-nofeature-ha” is used for deploying multinode openstack (virtual1)
# Scenario (-s parameter): “os-nosdn-nofeature-noha” used for deploying all-in-one openstack (virtual2)

# more details on deploy.sh OPTIONS:
#   -B  PXE Bridge for booting Daisy Master, optional
#   -D  Dry-run, does not perform deployment, will be deleted later
#   -L  Securelab repo absolute path, optional
#   -l  LAB name, necessary
#   -p  POD name, necessary
#   -r  Remote workspace in target server, optional
#   -w  Workdir for temporary usage, optional
#   -h  Print this message and exit
#   -s  Deployment scenario
#   -S  Skip recreate Daisy VM during deployment

# When deployed successfully, the floating IP of openstack is 10.20.11.11, the login account is “admin” and the password is “keystone”
