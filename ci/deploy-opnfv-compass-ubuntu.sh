#!/usr/bin/env bash

# /usr/bin/env bash or /bin/bash ? /usr/bin/env bash is more environment-independent
# beware of files which were edited in Windows, and have invisible \r end-of-line characters, causing Linux errors

# localization control: force script to use default language for output, and force sorting to be bytewise
# ("C" is from C language, represents "safe" locale everywhere)
# (result: the script will consider only basic ASCII characters and disable UTF-8 multibyte match)
export LANG=C
export LC_ALL=C

#################################################################################
## installation of OpenStack via OPNFV Compass4nfv, on Ubuntu, virtual deployment
#################################################################################
# reference manual: https://docs.opnfv.org/en/latest/submodules/compass4nfv/docs/release/installation/index.html
# page for virtual deployment: https://docs.opnfv.org/en/latest/submodules/compass4nfv/docs/release/installation/vmdeploy.html

echo "*** begin AUTO install: OPNFV Compass4nfv"

# prepare install directory
export INSTALLDIR=/opt/opnfv-compass
mkdir -p $INSTALLDIR
cd $INSTALLDIR

# premptively install latest pip and clear $PATH cache
sudo apt -y install python-pip
pip install --upgrade pip
hash -r
sudo apt -y autoremove


# 2 options: (option 1 is preferable)
# 1) remain in master branch, use build.sh (which builds a tar ball), then launch deploy.sh
# 2) download a tar ball and launch deploy.sh in a branch matching the tar ball release (e.g. fraser 6.2)


##############
# OPTION 1: build.sh + deploy.sh in master branch

# retrieve the repository of Compass4nfv code (this creates a compass4nfv subdir in the installation directory), current master branch
echo "*** begin download Compass4nfv repository"
git clone https://gerrit.opnfv.org/gerrit/compass4nfv
cd compass4nfv

# launch build script
echo "*** begin Compass4nfv build:"
./build.sh |& tee log1-Build.txt

# edit in deploy.sh specific to OPTION 1
# set path to ISO file (tar ball), as built by build.sh previously
# absolute path to tar ball file URL (MUST be absolute path)
sed -i '/#export TAR_URL=/a export TAR_URL=file:///opt/opnfv-compass/compass4nfv/work/building/compass.tar.gz' deploy.sh

# END OPTION 1
##############


##############
# OPTION 2: tar ball + deploy.sh in matching releases/branches

# download tarball of a certain release/version
#echo "*** begin download Compass4nfv tar ball"
#wget http://artifacts.opnfv.org/compass4nfv/fraser/opnfv-6.2.tar.gz
# note: list of tar ball (ISO) files from Compass4NFV in https://artifacts.opnfv.org/compass4nfv.html

# retrieve the repository of Compass4nfv code (this creates a compass4nfv subdir in the installation directory), current master branch
#echo "*** begin download Compass4nfv repository"
#git clone https://gerrit.opnfv.org/gerrit/compass4nfv
#cd compass4nfv
# note: list of compass4nfv branch names in https://gerrit.opnfv.org/gerrit/#/admin/projects/compass4nfv,branches
# checkout to branch (or tag) matching the tarball release
#git checkout stable/fraser

# edit in deploy.sh specific to OPTION 2
# set path to ISO file (tar ball), as downloaded previously
# absolute path to tar ball file URL (MUST be absolute path)
# sed -i '/#export TAR_URL=/a export TAR_URL=file:///opt/opnfv-compass/opnfv-6.2.tar.gz' deploy.sh

# END OPTION 2
##############


# edit remaining deploy.sh entries as needed

# set operating system version: Ubuntu Xenial Xerus
sed -i '/#export OS_VERSION=xenial\/centos7/a export OS_VERSION=xenial' deploy.sh

# set path to OPNFV scenario / DHA (Deployment Hardware Adapter) YAML file
# here, os-nosdn-nofeature-noha scenario
sed -i '/#export DHA=/a export DHA=/opt/opnfv-compass/compass4nfv/deploy/conf/vm_environment/os-nosdn-nofeature-noha.yml' deploy.sh

# set path to network YAML file
sed -i '/#export NETWORK=/a export NETWORK=/opt/opnfv-compass/compass4nfv/deploy/conf/vm_environment/network.yml' deploy.sh

# append parameters for virtual machines (for virtual deployments); e.g., 2 nodes for NOHA scenario, 5 for HA, etc.
# note: this may not be needed in a future release of Compass4nfv

# VIRT_NUMBER – the number of nodes for virtual deployment.
# VIRT_CPUS – the number of CPUs allocated per virtual machine.
# VIRT_MEM – the memory size (MB) allocated per virtual machine.
# VIRT_DISK – the disk size allocated per virtual machine.

# if OPTION 1 (master): OPENSTACK_VERSION is queens, so add the VIRT_NUMBER line after the queens match
#sed -i '/export OPENSTACK_VERSION=queens/a export VIRT_DISK=200G' deploy.sh
#sed -i '/export OPENSTACK_VERSION=queens/a export VIRT_MEM=16384' deploy.sh
#sed -i '/export OPENSTACK_VERSION=queens/a export VIRT_CPUS=4' deploy.sh
sed -i '/export OPENSTACK_VERSION=queens/a export VIRT_NUMBER=2' deploy.sh

# if OPTION 2 (stable/fraser): OPENSTACK_VERSION is pike, so add the VIRT_NUMBER line after the pike match
#sed -i '/export OPENSTACK_VERSION=pike/a export VIRT_DISK=200G' deploy.sh
#sed -i '/export OPENSTACK_VERSION=pike/a export VIRT_MEM=16384' deploy.sh
#sed -i '/export OPENSTACK_VERSION=pike/a export VIRT_CPUS=4' deploy.sh
#sed -i '/export OPENSTACK_VERSION=pike/a export VIRT_NUMBER=5' deploy.sh


# launch deploy script
echo "*** begin Compass4nfv deploy:"
./deploy.sh |& tee log2-Deploy.txt




# To access OpenStack Horizon GUI in Virtual deployment
# source: https://wiki.opnfv.org/display/compass4nfv/Containerized+Compass

# confirm IP@ of the current server (jump server, such as 10.10.100.xyz on LaaS: 10.10.100.42 for hpe32, etc.)
external_nic=`ip route |grep '^default'|awk '{print $5F}'`
echo "external_nic: $external_nic"
ip addr show $external_nic

# Config IPtables rules: pick an unused port number, e.g. 50000+machine number, 50032 for hpe32 at 10.10.100.42
# 192.16.1.222:443 is the OpenStack Horizon GUI after a Compass installation
# syntax: iptables -t nat -A PREROUTING -d $EX_IP -p tcp --dport $PORT -j DNAT --to 192.16.1.222:443
# (note: this could be automated: retrieve IP@, pick port number)
iptables -t nat -A PREROUTING -d 10.10.100.25 -p tcp --dport 50015 -j DNAT --to 192.16.1.222:443

# Enter https://$EX_IP:$PORT in you browser to visit the OpenStack Horizon dashboard
# example: https://10.10.100.25:50015
# The default user is "admin"
# to get the Horizon password for "admin":
sudo docker cp compass-tasks:/opt/openrc ./
sudo cat openrc | grep OS_PASSWORD


echo "*** end AUTO install: OPNFV Compass4nfv"

