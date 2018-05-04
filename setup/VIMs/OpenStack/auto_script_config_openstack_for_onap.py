#!/usr/bin/env python3

# ===============LICENSE_START=======================================================
# Apache-2.0
# ===================================================================================
# Copyright (C) 2018 Wipro. All rights reserved.
# ===================================================================================
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================


# OPNFV Auto project
# https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095

#docstring
"""This script configures an OpenStack instance to make it ready to interface with an ONAP instance, for example to host VM-based VNFs deployed by ONAP.
Auto project: https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095
"""

######################################################################
# This script configures an OpenStack instance (e.g. from an OPNFV installer like FUEL/MCP) to make it
# ready to interface with an ONAP instance, for example to host VM-based VNFs deployed by ONAP.
# After running this script, the created OpenStack object names/IDs can be used for example to populate
# YAML&ENV files used by ONAP (installation of ONAP itself, VNF descriptor files, etc.).


######################################################################
# Overview of the steps:
#
# 1) create an ONAP project/tenant (a tenant is a project; project is a more generic term than tenant)
#   (optional, probably not needed: create a new group, which can be associated to a project, and contains users)
# 2) create an ONAP user within the ONAP project, so as not to use the "admin" user for ONAP
#   (associate user to group if applicable; credentials: name/pwd or name/APIkey, or token)
# 3) create an ONAP security group, to allow ICMP traffic (for pings) and TCP port 22 (for SSH), rather than changing default security group(s)
#   (optional, probably not needed: create new region)
# 4a) create a public network for ONAP VNFs, with ports, subnet, and CIDR block
#    (or maybe not necessary? floating_net serves as public/external network and provides pool of floating IP@)
# 4b) create an OAM network for ONAP VNFs, with ports, subnet, and CIDR block
#    (ONAP VNFs will be deployed in this OMA/private network, which will be connected by router to an external network)
# 5) create an OpenStack router, with an interface to the OAM/private network (and one to the public network?)
#    and a reference to an external network (gateway)
# 6) create VM flavors as needed: m1.medium, etc.
# 7) download images, as needed for ONAP-deployed VNFs: e.g. Ubuntu 14.04, 16.04, ...


######################################################################
# Assumptions:
# - python3 is installed
# - OpenStack SDK is installed for python3
# - there is a clouds.yaml file (describing the OpenStack instance, especially the Auth URL and admin credentials)
# - the script connects to OpenStack as a user with admin rights

# typical commands to install OpenStack SDK Python client:
# apt install python3-pip
# pip3 install --upgrade pip
# pip3 list
# pip3 install openstacksdk
# pip3 install --upgrade openstacksdk
# pip3 show openstacksdk
# pip3 check


######################################################################
# useful URLs
# Identity API: https://docs.openstack.org/openstacksdk/latest/user/proxies/identity_v3.html
#   (User, Project, Group, region, Role, ...)
# Network API:  https://docs.openstack.org/openstacksdk/latest/user/proxies/network.html
#   (Network, Subnet, Port, Router, Floating IP, AZ, Flavor, ...)


######################################################################
# script parameters
ONAP_USER_NAME          = 'onap_user'
ONAP_USER_PASSWORD      = 'auto_topsecret'
ONAP_USER_DESC          = 'OpenStack User created for ONAP'

ONAP_TENANT_NAME        = 'onap_tenant'  # "project" is a more generic concept than "tenant"; a tenant is type of project
ONAP_TENANT_DESC        = 'OpenStack Project/Tenant created for ONAP'

ONAP_SECU_GRP_NAME      = 'ONAP security group'
ONAP_SECU_GRP_DESC      = 'Security Group for ONAP'

ONAP_PUBLIC_NET_NAME    = 'onap_public_net'
ONAP_PUBLIC_SUBNET_NAME = 'onap_public_subnet'
ONAP_PUBLIC_SUBNET_CIDR = '10.0.0.0/16'
ONAP_PUBLIC_NET_DESC    = 'Public network created for ONAP'

ONAP_OAM_NET_NAME       = 'onap_oam_net'
ONAP_OAM_SUBNET_NAME    = 'onap_oam_subnet'
ONAP_OAM_SUBNET_CIDR    = '192.168.30.0/24'
ONAP_OAM_NET_DESC       = 'OAM network created for ONAP'

ONAP_ROUTER_NAME        = 'onap_router'
ONAP_ROUTER_DESC        = 'Router created for ONAP'

EXTERNAL_NETWORK_NAME   = 'floating_net'  # external network (gateway) name to be used in OpenStack instance

# OpenStack cloud name and region name, which should be the same as in the clouds.yaml file used by this script
OPENSTACK_CLOUD_NAME    = 'hpe16openstackFraser'
OPENSTACK_REGION_NAME   = 'RegionOne'
# OpenStack domain is: Default


######################################################################
# constants which could be parameters
DNS_SERVER_IP           = '8.8.8.8'
# IP addresses of free public DNS service from Google:
# - IPv4: 8.8.8.8 and 8.8.4.4
# - IPv6: 2001:4860:4860::8888 and 2001:4860:4860::8844


######################################################################
# import statements
import openstack
import argparse


######################################################################
def delete_all_ONAP():
    """Delete all ONAP-specific OpenStack objects (normally not needed, but may be useful during tests)."""
    print("\nOPNFV Auto, script to delete ONAP objects in an OpenStack instance")

    try:
        # connect to OpenStack instance using Connection object from OpenStack SDK
        conn = openstack.connect(cloud=OPENSTACK_CLOUD_NAME, region_name=OPENSTACK_REGION_NAME)

        # delete router; must delete router before networks.
        onap_router  = conn.network.find_router(ONAP_ROUTER_NAME)
        print('DEBUG onap_router:\n',onap_router,'\n\n')
        if onap_router != None:
            print('Deleting ONAP router...')
            conn.network.delete_router(onap_router.id)
        else:
            print('No ONAP router found...')

        # delete OAM network (which should also delete associated subnet and ports if any)
        oam_network = conn.network.find_network(ONAP_OAM_NET_NAME)
        print('DEBUG oam_network:\n',oam_network,'\n\n')
        if oam_network != None:
            print('Deleting ONAP OAM network...')
            conn.network.delete_network(oam_network.id)
        else:
            print('No ONAP OAM network found...')

        # delete public network (which should also delete associated subnet and ports if any)
        public_network = conn.network.find_network(ONAP_PUBLIC_NET_NAME)
        print('DEBUG public_network:\n',public_network,'\n\n')
        if public_network != None:
            print('Deleting ONAP public network...')
            conn.network.delete_network(public_network.id)
        else:
            print('No ONAP public network found...')

        # delete security group
        onap_security_group = conn.network.find_security_group(ONAP_SECU_GRP_NAME)
        print('DEBUG onap_security_group:\n',onap_security_group,'\n\n')
        if onap_security_group != None:
            print('Deleting ONAP security group...')
            conn.network.delete_security_group(onap_security_group.id)
        else:
            print('No ONAP security group found...')

        # # delete user
        # onap_user = conn.identity.find_user(ONAP_USER_NAME)
        # if onap_user != None:
            # print('Deleting ONAP user...')
            # conn.identity.delete_user(onap_user.id)
        # else:
            # print('No ONAP user found...')

        # # delete project/tenant
        # onap_project = conn.identity.find_project(ONAP_TENANT_NAME)
        # if onap_project != None:
            # print('Deleting ONAP project...')
            # conn.identity.delete_project(onap_project.id)
        # else:
            # print('No ONAP project found...')

    except Exception as e:
        print("Exception:",type(e), e)
        print("[Script terminated]\n")

    print("OPNFV Auto, end of deletion script\n")


######################################################################
def configure_all_ONAP():
    """Configure all ONAP-specific OpenStack objects."""
    print("\nOPNFV Auto, script to configure an OpenStack instance for ONAP")

    try:
        # connect to OpenStack instance using Connection object from OpenStack SDK
        print('Opening connection...')
        conn = openstack.connect(cloud=OPENSTACK_CLOUD_NAME, region_name=OPENSTACK_REGION_NAME)


        # TESTS: IGNORE/DELETE (BEGIN)
        # gdserver_ID = '8bc274a2-8c0d-4795-9b4d-faa0a21e1d88'
        # gdserver = conn.compute.get_server(gdserver_ID)
        # print('\ngdserver.name=',gdserver.name)
        # print('gdserver.status=',gdserver.status)

        # # print("\nList Users:")
        # # i=1
        # # for user in conn.identity.users():
            # # print('User',str(i),'\n',user,'\n')
            # # i+=1

        # # print("\nList Projects:")
        # # i=1
        # # for project in conn.identity.projects():
            # # print('Project',str(i),'\n',project,'\n')
            # # i+=1

        # print("\nList Networks:")
        # i=1
        # for network in conn.network.networks():
            # print('Network',str(i),'\n',network,'\n')
            # i+=1

        # print("\nList Flavors:")
        # i=1
        # for flvr in conn.compute.flavors():
            # print('Flavor',str(i),'\n',flvr,'\n')
            # i+=1

        # print("\nList Images:")
        # i=1
        # for img in conn.compute.images():
            # print('Image',str(i),'\n',img,'\n')
            # i+=1

        # router = conn.network.find_router('gd_test_router')
        # print('gd router\n',router,'\n\n')
        # router = conn.network.find_router('e4e59f63-8063-4774-a97a-c110c6969e4a')
        # print('gd router\n',router,'\n\n')
        # TESTS: IGNORE/DELETE (END)



        # TODO: find out why conn.identity does not exist @@@
        # onap_project = conn.identity.find_project(ONAP_TENANT_NAME)
        # if onap_project != None:
            # print('ONAP project/tenant already exists')
        # else:
            # print('Creating ONAP project/tenant...')
            # onap_project = conn.identity.create_project(
                # name = ONAP_TENANT_NAME,
                # description = ONAP_TENANT_DESC,
                # is_enabled = True)
                # # domain: leave default
                # # project quotas (max #vCPUs, #instances, etc.): as conn.network.<*quota*>, using project id for quota id
                # # https://docs.openstack.org/openstacksdk/latest/user/proxies/network.html#quota-operations
                # # https://docs.openstack.org/openstacksdk/latest/user/resources/network/v2/quota.html#openstack.network.v2.quota.Quota
                # # conn.network.update_quota(project_id = onap_project.id)
                # # SDK for quotas supports floating_ips, networks, ports, etc. but not vCPUs or instances
            # print('DEBUG onap_project:\n',onap_project,'\n\n')

        # onap_user= conn.identity.find_user(ONAP_USER_NAME)
        # if onap_user != None:
            # print('ONAP user already exists')
        # else:
            # print('Creating ONAP user...')
            # onap_user = conn.identity.create_user(
                # name = ONAP_USER_NAME,
                # description = ONAP_USER_DESC,
                # default_project_id  = onap_project.id,
                # password = ONAP_USER_PASSWORD,
                # is_enabled = True)
                # # domain: leave default
                # # default_project_id: primary project
            # print('DEBUG onap_user:\n',onap_user,'\n\n')



        # make sure security group allows ICMP (for ping) and SSH (TCP port 22) traffic; also IPv4/v6 traffic ingress and egress
        # create new onap_security_group (or maybe just "default" security group ? tests returned multiple "default" security groups)
        # security group examples: check http://git.openstack.org/cgit/openstack/openstacksdk/tree/examples/network/security_group_rules.py
        # if rule already exists, OpenStack returns an error, so just try (no harm); try each separately
        onap_security_group = conn.network.find_security_group(ONAP_SECU_GRP_NAME)
        if onap_security_group == None:
            onap_security_group = conn.network.create_security_group(
                # project_id  = onap_project.id,
                description = ONAP_SECU_GRP_DESC,
                name        = ONAP_SECU_GRP_NAME)
        else:
            print('ONAP security group already exists')
            print('DEBUG onap_security_group:\n',onap_security_group,'\n\n')

        try:
            description_text = 'enable ICMP ingress IPv4'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = 'ICMP',
                direction           = 'ingress',
                ethertype           = 'IPv4',
                remote_ip_prefix    = '0.0.0.0/0',
                port_range_min      = None,
                port_range_max      = None)
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        try:
            description_text = 'enable ICMP egress IPv4'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = 'ICMP',
                direction           = 'egress',
                ethertype           = 'IPv4',
                remote_ip_prefix    = '0.0.0.0/0',
                port_range_min      = None,
                port_range_max      = None)
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        try:
            description_text = 'enable SSH (TCP port 22) ingress IPv4'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = 'TCP',
                direction           = 'ingress',
                ethertype           = 'IPv4',
                remote_ip_prefix    = '0.0.0.0/0',
                port_range_min      = '22',
                port_range_max      = '22')
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        try:
            description_text = 'enable SSH (TCP port 22) egress IPv4'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = 'TCP',
                direction           = 'egress',
                ethertype           = 'IPv4',
                remote_ip_prefix    = '0.0.0.0/0',
                port_range_min      = '22',
                port_range_max      = '22')
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        try:
            description_text = 'enable IP traffic ingress IPv4'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = None,
                direction           = 'ingress',
                ethertype           = 'IPv4',
                remote_ip_prefix    = '0.0.0.0/0',
                port_range_min      = None,
                port_range_max      = None)
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        try:
            description_text = 'enable IP traffic ingress IPv6'
            print('Creating rule:',description_text,'...')
            conn.network.create_security_group_rule(
                security_group_id   = onap_security_group.id,
                description         = description_text,
                protocol            = None,
                direction           = 'ingress',
                ethertype           = 'IPv6',
                remote_ip_prefix    = '::/0',
                port_range_min      = None,
                port_range_max      = None)
        except Exception as e:
            print(description_text, ' Exception:', type(e), e)

        # IPv4 IP egress rule should already exist by default
        # try:
            # description_text = 'enable IP traffic egress IPv4'
            # print('Creating rule:',description_text,'...')
            # conn.network.create_security_group_rule(
                # security_group_id   = onap_security_group.id,
                # description         = description_text,
                # protocol            = None,
                # direction           = 'egress',
                # ethertype           = 'IPv4',
                # remote_ip_prefix    = '0.0.0.0/0',
                # port_range_min      = None,
                # port_range_max      = None)
        # except Exception as e:
            # print(description_text, ' Exception:', type(e), e)

        # IPv6 IP egress rule should already exist by default
        # try:
            # description_text = 'enable IP traffic egress IPv6'
            # print('Creating rule:',description_text,'...')
            # conn.network.create_security_group_rule(
                # security_group_id   = onap_security_group.id,
                # description         = description_text,
                # protocol            = None,
                # direction           = 'egress',
                # ethertype           = 'IPv6',
                # remote_ip_prefix    = '::/0',
                # port_range_min      = None,
                # port_range_max      = None)
        # except Exception as e:
            # print(description_text, ' Exception:', type(e), e)


        # public network
        public_network = conn.network.find_network(ONAP_PUBLIC_NET_NAME)
        if public_network != None:
            print('ONAP public network already exists')
        else:
            print('Creating ONAP public network...')
            public_network = conn.network.create_network(
                name = ONAP_PUBLIC_NET_NAME,
                description = ONAP_PUBLIC_NET_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True,
                is_shared = True)
                # subnet_ids = []: not needed, subnet refers to network_id
            print('DEBUG public_network:\n',public_network,'\n\n')

            print('Creating subnetwork for ONAP public network...')
            public_subnet = conn.network.create_subnet(
                name = ONAP_PUBLIC_SUBNET_NAME,
                #project_id = onap_project.id,
                network_id = public_network.id,
                cidr = ONAP_PUBLIC_SUBNET_CIDR,
                ip_version = 4,
                is_dhcp_enabled = True,
                dns_nameservers = [DNS_SERVER_IP])    # list of DNS IP@
            print('DEBUG public_network:\n',public_network,'\n\n')
            print('DEBUG public_subnet:\n',public_subnet,'\n\n')


        # OAM network
        oam_network = conn.network.find_network(ONAP_OAM_NET_NAME)
        if oam_network != None:
            print('ONAP OAM network already exists')
        else:
            print('Creating ONAP OAM network...')
            oam_network = conn.network.create_network(
                name = ONAP_OAM_NET_NAME,
                description = ONAP_OAM_NET_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True,
                is_shared = True)
            print('DEBUG oam_network:\n',oam_network,'\n\n')

            print('Creating subnetwork for ONAP OAM network...')
            oam_subnet = conn.network.create_subnet(
                name = ONAP_OAM_SUBNET_NAME,
                #project_id = onap_project.id,
                network_id = oam_network.id,
                cidr = ONAP_OAM_SUBNET_CIDR,
                ip_version = 4,
                is_dhcp_enabled = True,
                dns_nameservers = [DNS_SERVER_IP])    # list of DNS IP@; maybe not needed for OAM network
            print('DEBUG oam_network:\n',oam_network,'\n\n')
            print('DEBUG oam_subnet:\n',oam_subnet,'\n\n')


        # router
        onap_router = conn.network.find_router(ONAP_ROUTER_NAME)
        if onap_router != None:
            print('ONAP router already exists')
        else:
            print('Creating ONAP router...')
            onap_router = conn.network.create_router(
                name = ONAP_ROUTER_NAME,
                description = ONAP_ROUTER_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True)
            print('DEBUG onap_router:\n',onap_router,'\n\n')

            # add interfaces to ONAP networks: Public and OAM
            # syntax: add_interface_to_router(router, subnet_id=None, port_id=None)
            print('Adding interfaces to ONAP router for ONAP public and OAM networks...')
            conn.network.add_interface_to_router(onap_router, subnet_id = public_subnet.id)
            conn.network.add_interface_to_router(onap_router, subnet_id = oam_subnet.id)
            print('DEBUG onap_router:\n',onap_router,'\n\n')

            # not public network, but external network like floating_net
            # point to ONAP Public Network as external network (i.e. Gateway); network_id is passed in a body dictionary
            # syntax: add_gateway_to_router(router, **body)
            print('Adding external network (gateway) to ONAP router...')

            # nope
            # network_dict_body = {'network_id': public_network.id}
            # nope
            # network_dict_body = {
                # 'external_fixed_ips': [{'subnet_id' : public_subnet.id}],
                # 'network_id': public_network.id
            # }
            external_network = conn.network.find_network(EXTERNAL_NETWORK_NAME)
            print('DEBUG external_network:\n',external_network,'\n\n')
            #network_dict_body = {'gateway' : {'network_id' : external_network.id}}
            #conn.network.add_gateway_to_router(onap_router, body=network_dict_body)
            conn.network.add_gateway_to_router(onap_router, network_id=external_network.id)


        # also create 5 flavors, from tiny to xlarge (hard-coded, no need for parameters)
        print('Creating flavors...')
        tiny_flavor = conn.compute.find_flavor("m1.tiny")
        if tiny_flavor != None:
            print('m1.tiny Flavor already exists')
        else:
            print('Creating m1.tiny Flavor...')
            tiny_flavor = conn.compute.create_flavor(
                name = 'm1.tiny',
                vcpus = 1,
                disk = 1,
                ram = 512,
                ephemeral = 0,
                #swap = 0,
                #rxtx_factor = 1.0,
                is_public = True)
            print('DEBUG tiny_flavor:\n',tiny_flavor,'\n\n')

        small_flavor = conn.compute.find_flavor("m1.small")
        if small_flavor != None:
            print('m1.small Flavor already exists')
        else:
            print('Creating m1.small Flavor...')
            small_flavor = conn.compute.create_flavor(
                name = 'm1.small',
                vcpus = 1,
                disk = 20,
                ram = 2048,
                ephemeral = 0,
                #swap = 0,
                #rxtx_factor = 1.0,
                is_public = True)
            print('DEBUG small_flavor:\n',small_flavor,'\n\n')

        medium_flavor = conn.compute.find_flavor("m1.medium")
        if medium_flavor != None:
            print('m1.medium Flavor already exists')
        else:
            print('Creating m1.medium Flavor...')
            medium_flavor = conn.compute.create_flavor(
                name = 'm1.medium',
                vcpus = 2,
                disk = 40,
                ram = 4096,
                ephemeral = 0,
                #swap = 0,
                #rxtx_factor = 1.0,
                is_public = True)
            print('DEBUG medium_flavor:\n',medium_flavor,'\n\n')

        large_flavor = conn.compute.find_flavor("m1.large")
        if large_flavor != None:
            print('m1.large Flavor already exists')
        else:
            print('Creating m1.large Flavor...')
            large_flavor = conn.compute.create_flavor(
                name = 'm1.large',
                vcpus = 4,
                disk = 80,
                ram = 8192,
                ephemeral = 0,
                #swap = 0,
                #rxtx_factor = 1.0,
                is_public = True)
            print('DEBUG large_flavor:\n',large_flavor,'\n\n')

        xlarge_flavor = conn.compute.find_flavor("m1.xlarge")
        if xlarge_flavor != None:
            print('m1.xlarge Flavor already exists')
        else:
            print('Creating m1.xlarge Flavor...')
            xlarge_flavor = conn.compute.create_flavor(
                name = 'm1.xlarge',
                vcpus = 8,
                disk = 160,
                ram = 16384,
                ephemeral = 0,
                #swap = 0,
                #rxtx_factor = 1.0,
                is_public = True)
            print('DEBUG xlarge_flavor:\n',xlarge_flavor,'\n\n')



        # also create 3 images, Ubuntu 16.04, 14.04, CirrOS
        # 64-bit QCOW2 image for cirros-0.4.0-x86_64-disk.img
        # description: CirrOS minimal Linux distribution
        # http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
        # user/password: cirros/gocubsgo

        # 64-bit QCOW2 image for Ubuntu 16.04 is xenial-server-cloudimg-amd64-disk1.img
        # description: Ubuntu Server 16.04 LTS (Xenial Xerus)
        # https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-disk1.img
        # user: ubuntu

        # 64-bit QCOW2 image for Ubuntu 14.04 is trusty-server-cloudimg-amd64-disk1.img
        # description: Ubuntu Server 14.04 LTS (Trusty Tahr)
        # http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
        # user: ubuntu


        # IMAGE_NAME = 'cirros-0.4.0-x86_64-disk.img'
        # cirros040 = conn.compute.find_image(IMAGE_NAME)
        # if cirros040 != None:
            # print(IMAGE_NAME,'Image already exists')
        # else:
            # print('Creating',IMAGE_NAME,'Image ...')
            # # no conn.compute.create_image() method yet in OpenStack SDK... unless doc is wrong ?
            # cirros040 = conn.compute.create_image(
                # name = IMAGE_NAME)
            # # no support for URL download ? maybe with Image.metadata, or with ImageDetail class ?
            # print('DEBUG cirros040:\n',cirros040,'\n\n')




    except Exception as e:
        print("Exception:",type(e), e)
        print("[Script terminated]\n")


    print("OPNFV Auto, end of configuration script\n")



######################################################################
def main():

    # configure argument parser: one optional argument
    # if no "-d" or "--delete" option, then configure OpenStack for ONAP
    # with "-d" or "--delete" option, then delete ONAP configuration in OpenStack
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete",
        help = "delete ONAP configuration",
        action = "store_true")

    # parse arguments and use corresponding script
    args = parser.parse_args()
    if args.delete:
        delete_all_ONAP()
    else:
        configure_all_ONAP()


if __name__ == "__main__":
    main()

