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

##################################################################################
## installation of OpenStack via OPNFV Apex/TripleO, on CentOS, virtual deployment
##################################################################################
# reference manual: https://docs.opnfv.org/en/latest/submodules/apex/docs/release/installation/index.html
# page for virtual deployment: https://docs.opnfv.org/en/latest/submodules/apex/docs/release/installation/virtual.html

echo "*** begin AUTO install: OPNFV Apex/TripleO"

# check OS version
echo "*** print OS version (must be CentOS, version 7 or more)"
cat /etc/*release

# Manage Nested Virtualization
echo "*** ensure Nested Virtualization is enabled on Intel x86"
echo "***   nested flag before:"
cat /sys/module/kvm_intel/parameters/nested
rm -f /etc/modprobe.d/kvm-nested.conf
echo "options kvm-intel nested=1" >> /etc/modprobe.d/kvm-nested.conf
echo "options kvm-intel enable_shadow_vmcs=1" >> /etc/modprobe.d/kvm-nested.conf
echo "options kvm-intel enable_apicv=1" >> /etc/modprobe.d/kvm-nested.conf
echo "options kvm-intel ept=1" >> /etc/modprobe.d/kvm-nested.conf
sudo modprobe -r kvm_intel
sudo modprobe -a kvm_intel
echo "***   nested flag after:"
cat /sys/module/kvm_intel/parameters/nested

echo "*** verify status of modules in the Linux Kernel: kvm_intel module should be loaded for x86_64 machines"
lsmod | grep kvm_
cat /proc/modules |grep kvm_


# 3 additional pre-installation preparations, lifted from OPNFV/storperf (they are post-installation there):
# https://wiki.opnfv.org/display/storperf/LaaS+Setup+For+Development#LaaSSetupForDevelopment-InstallOPNFVApex
# (may of may not be needed, to enable first-time Apex installation on blank server)

# 1) Install Docker
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce
sudo systemctl start docker

# 2) Install docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3) Install Python
sudo yum install -y python-virtualenv
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel


# update everything (upgrade: riskier than update, as packages supposed to be unused will be deleted)
# (note: can take several minutes; may not be necessary)
sudo yum -y update


# download Apex packages
echo "*** downloading packages:"
sudo yum -y install https://repos.fedorapeople.org/repos/openstack/openstack-pike/rdo-release-pike-1.noarch.rpm
sudo yum -y install epel-release
# note: EPEL = Extra Packages for Enterprise Linux
sudo curl -o /etc/yum.repos.d/opnfv-apex.repo http://artifacts.opnfv.org/apex/fraser/opnfv-apex.repo

# install three required RPMs (RedHat/RPM Package Managers); this takes several minutes
sudo yum -y install http://artifacts.opnfv.org/apex/fraser/opnfv-apex-6.2.noarch.rpm http://artifacts.opnfv.org/apex/fraser/opnfv-apex-undercloud-6.2.noarch.rpm http://artifacts.opnfv.org/apex/fraser/opnfv-apex-python34-6.2.noarch.rpm

# clean-up old Apex versions if any
## precautionary opnfv-clean doesn't work... (even though packages are installed at this point)
opnfv-clean

# Manage DNS references
# probably not needed on an already configured server: already has DNS references
# echo "nameserver 8.8.8.8" >> /etc/resolv.conf
echo "*** printout of /etc/resolv.conf :"
cat /etc/resolv.conf

# prepare installation directory
mkdir -p /opt/opnfv-TripleO-apex
cd /opt/opnfv-TripleO-apex

# make sure cp is not aliased or a function; same for mv and rm
unalias cp
unset -f cp
unalias mv
unset -f mv
unalias rm
unset -f rm

# 2 YAML files from /etc/opnfv-apex/ are needed for virtual deploys:
# 1) network_settings.yaml : may need to update NIC names, to match the NIC names on the deployment server
# 2) standard scenario file (os-nosdn-nofeature-noha.yaml, etc.), or customized deploy_settings.yaml

# make a local copy of YAML files (not necessary: could deploy from /etc/opnfv-apex); local copies are just for clarity
# 1) network settings
cp /etc/opnfv-apex/network_settings.yaml .
# 2) deploy settings
# copy one of the 40+ pre-defined scenarios (one of the YAML files)
# for extra customization, git clone Apex repo, and copy and customize the generic deploy_settings.yaml
# git clone https://git.opnfv.org/apex
# cp ./apex/config/deploy/deploy_settings.yaml .
cp /etc/opnfv-apex/os-nosdn-nofeature-noha.yaml ./deploy_settings.yaml
# cp /etc/opnfv-apex/os-nosdn-nofeature-ha.yaml ./deploy_settings.yaml

# Note: content of os-nosdn-nofeature-noha.yaml
# ---
# global_params:
#   ha_enabled: false
#
# deploy_options:
#   sdn_controller: false
#   tacker: true
#  congress: true
#   sfc: false
#   vpn: false


# modify NIC names in network settings YAML file, specific to your environment (e.g. replace em1 with ens4f0 in LaaS)
# Note: actually, this should not matter for a virtual environment
sed -i 's/em1/ens4f0/' network_settings.yaml

# launch deploy (works if openvswitch module is installed, which may not be the case the first time around)
echo "*** deploying OPNFV by TripleO/Apex:"
# --debug for detailed debug info
# -v: Enable virtual deployment
# note: needs at least 10G RAM for controllers
sudo opnfv-deploy --debug -v -n network_settings.yaml -d deploy_settings.yaml
# without --debug:
# sudo opnfv-deploy -v -n network_settings.yaml -d deploy_settings.yaml

# with specific sizing:
# sudo opnfv-deploy --debug -v -n network_settings.yaml -d deploy_settings.yaml --virtual-compute-ram 32 --virtual-cpus 16 --virtual-computes 4


# verify that the openvswitch module is listed:
lsmod | grep openvswitch
cat /proc/modules |grep openvswitch


##{
## workaround: do 2 successive installations... not exactly optimal...
## clean up, as now opnfv-clean should work
#opnfv-clean
## second deploy try, should succeed (whether first one failed or succeeded)
#sudo opnfv-deploy -v -n network_settings.yaml -d deploy_settings.yaml
##}



# verifications: https://docs.opnfv.org/en/latest/submodules/apex/docs/release/installation/verification.html

# {
# if error after deploy.sh: "libvirt.libvirtError: Storage pool not found: no storage pool with matching name 'default'"

# This usually happens if for some reason you are missing a default pool in libvirt:
# $ virsh pool-list |grep default
# You can recreate it manually:
# $ virsh pool-define-as default dir --target /var/lib/libvirt/images/
# $ virsh pool-autostart default
# $ virsh pool-start default
# }

# {
# if error after deploy.sh: iptc.ip4tc.IPTCError
# check Apex jira ticket #521 https://jira.opnfv.org/browse/APEX-521
# }

# OpenvSwitch should not be missing, as it is a requirement from the RPM package:
# https://github.com/opnfv/apex/blob/stable/fraser/build/rpm_specs/opnfv-apex-common.spec#L15



# install python 3 on CentOS
echo "*** begin install python 3.6 (3.4 should be already installed by default)"

sudo yum -y install python36
# install pip and setup tools
sudo curl -O https://bootstrap.pypa.io/get-pip.py
hash -r
sudo /usr/bin/python3.6 get-pip.py --no-warn-script-location



echo "*** end AUTO install: OPNFV Apex/TripleO"

