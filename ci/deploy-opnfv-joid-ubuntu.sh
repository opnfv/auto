#!/usr/bin/env bash

# /usr/bin/env bash or /bin/bash ? /usr/bin/env bash is more environment-independent
# beware of files which were edited in Windows, and have invisible \r end-of-line characters, causing Linux errors

# localization control: force script to use default language for output, and force sorting to be bytewise
# ("C" is from C language, represents "safe" locale everywhere)
# (result: the script will consider only basic ASCII characters and disable UTF-8 multibyte match)
export LANG=C
export LC_ALL=C

#########################################################################
## installation of OpenStack via OPNFV JOID, on Ubuntu, virtual deployment
#########################################################################
# reference manual: https://docs.opnfv.org/en/stable-fraser/submodules/joid/docs/release/installation/index.html
# page for virtual deployment: https://docs.opnfv.org/en/latest/submodules/joid/docs/release/installation/installation_virtual.html
# (JOID: Juju OPNFV Infrastructure Deployer)

echo "*** begin AUTO install: OPNFV JOID (Juju OPNFV Infrastructure Deployer)"

# prepare install directory
export INSTALLDIR=/opt/opnfv-joid
mkdir -p $INSTALLDIR
cd $INSTALLDIR

# Install git and bridge-utils packages
sudo apt install git bridge-utils

# retrieve JOID repository, current master branch; (this creates a joid subdir in the installation directory)
echo "*** begin download JOID repository"
git clone https://gerrit.opnfv.org/gerrit/p/joid.git
cd joid/ci

# initial pre-config (trial and error...)
sudo apt-get update -y
sudo apt -y autoremove

# Run the MAAS (Metal as a Service) deployment for virtual deployment without customized labconfig file
echo "*** MAAS (Metal as a Service) deployment"
./03-maasdeploy.sh

# expected final message:
# "MAAS deployment finished successfully"


# Run JOID deployment with configuration parameters:
# deploy.sh usage:
#   [-s|--sdn <nosdn|odl|ocl>]
#   [-t|--type <noha|ha|tip>]
#   [-o|--openstack <ocata|queens>]
#   [-l|--lab <default|custom>]
#   [-f|--feature <ipv6,dpdk,lxd,dvr,openbaton,multus>]
#   [-d|--distro <xenial>]
#   [-a|--arch <amd64|ppc64el|aarch64>]
#   [-m|--model <openstack|kubernetes>]
#   [-i|--virtinstall <0|1>]
#   [--maasinstall <0|1>]
#   [--labfile <labconfig.yaml file>]
#   [-r|--release <e>]

# example from user manual: corresponds to OPNFV scenario k8-nosdn-nofeature-noha
#echo "*** JOID-based k8-nosdn-nofeature-noha deployment, virtual"
#./deploy.sh -d xenial -s nosdn -t noha -f none -m kubernetes -l default -i 1

# os-nosdn-nofeature-noha, virtual install, x86/AMD64, OpenStack Queens, Ubuntu 16.04 Xenial Xerus VM image:
echo "*** JOID-based os-nosdn-nofeature-noha deployment, virtual, x86"
./deploy.sh -m openstack -s nosdn -f none -t noha -o queens -a amd64 -d xenial -l default -i 1

# os-nosdn-nofeature-ha, virtual install, x86/AMD64, OpenStack Queens, Ubuntu 16.04 Xenial Xerus VM image:
#echo "*** JOID-based os-nosdn-nofeature-ha deployment, virtual, x86"
#./deploy.sh -m openstack -s nosdn -f none -t ha -o queens -a amd64 -d xenial -l default -i 1


# expected final message:
# "Finished deployment and configuration"
# also displayed: local dashboard GUI URL, admin credentials


# verifications
echo "*** juju status"
juju status
echo "*** juju gui"
juju gui

juju status|grep keystone
juju status|grep dashboard

# OpenStack RC (runcom) file, enables OpenStack CLI commands
cat ~/joid_config/admin-openrc
source ~/joid_config/admin-openrc

openstack service list


# OpenStack Horizon :

# run in joid/ci directory; WARNING: must NOT be run by sudo or by root
# for OpenStack model:
#./setupproxy.sh openstack
# for Kubernetes model:
#./setupproxy.sh kubernetes

#chmod 777 setupproxy.sh
#./setupproxy.sh openstack

# 192.168.122.166:443 is the local Horizon GUI
iptables --table nat --list
iptables -t nat -L
# example: hpe33:
#iptables -t nat -A PREROUTING -d 10.10.100.43 -p tcp --dport 50033 -j DNAT --to 192.168.122.166:443
# in your browser: https://10.10.100.43:50033
# example: hpe31:
#iptables -t nat -A PREROUTING -d 10.10.100.41 -p tcp --dport 50031 -j DNAT --to 192.168.122.166:443
# in your browser: https://10.10.100.41:50031

iptables --table nat --list|grep 443



echo "*** end AUTO install: OPNFV JOID (Juju OPNFV Infrastructure Deployer)"

