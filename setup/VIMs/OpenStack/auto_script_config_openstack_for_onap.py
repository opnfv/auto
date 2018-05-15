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
#   (optional, probably not needed: create new region; default region RegionOne is OK)
# 4) create a public network for ONAP VNFs, with subnet and CIDR block
#    (so components have access to the Internet, via router and gateway, on unnamed ports, dynamic IP@ allocation)
# 5) create a private and an OAM network for ONAP VNFs or other ONAP components, with their respective subnet and CIDR block
#    (ONAP VNFs will be deployed in this private and/or OAM network(s), usually with named ports and static IP@ as per VNF configuration file)
# 6) create an OpenStack router, with interfaces to the public, private and OAM networks,
#    and a reference to an external network (gateway) provided by the OpenStack instance installation
# 7) create VM flavors as needed: m1.medium, etc.
# 8) download VM images, as needed for ONAP-deployed VNFs: e.g. Ubuntu 14.04, 16.04, ...


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
ONAP_USER_NAME              = 'ONAP_user'
ONAP_USER_PASSWORD          = 'auto_topsecret'
ONAP_USER_DESC              = 'OpenStack User created for ONAP'

ONAP_TENANT_NAME            = 'ONAP_tenant'  # "project" is a more generic concept than "tenant"; a tenant is type of project; quotas are per project;
ONAP_TENANT_DESC            = 'OpenStack Project/Tenant created for ONAP'

ONAP_SECU_GRP_NAME          = 'ONAP_security_group'
ONAP_SECU_GRP_DESC          = 'Security Group created for ONAP'

ONAP_PUBLIC_NET_NAME        = 'ONAP_public_net'
ONAP_PUBLIC_SUBNET_NAME     = 'ONAP_public_subnet'
ONAP_PUBLIC_SUBNET_CIDR     = '192.168.99.0/24'    # some arbitrary CIDR, but typically in a private (IANA-reserved) address range
ONAP_PUBLIC_NET_DESC        = 'Public network created for ONAP, for unnamed ports, dynamic IP@, access to the Internet (e.g., Nexus repo) via Gateway'

ONAP_PRIVATE_NET_NAME       = 'ONAP_private_net'
ONAP_PRIVATE_SUBNET_NAME    = 'ONAP_private_subnet'
ONAP_PRIVATE_SUBNET_CIDR    = '10.0.0.0/16'  # should match ONAP installation; Private and OAM may be the same network
ONAP_PRIVATE_NET_DESC       = 'Private network created for ONAP, for named ports, static IP@, inter-component communication'

ONAP_OAM_NET_NAME           = 'ONAP_OAM_net'
ONAP_OAM_SUBNET_NAME        = 'ONAP_OAM_subnet'
ONAP_OAM_SUBNET_CIDR        = '10.99.0.0/16'  # should match ONAP installation; Private and OAM may be the same network
ONAP_OAM_NET_DESC           = 'OAM network created for ONAP, for named ports, static IP@, inter-component communication'

ONAP_ROUTER_NAME            = 'ONAP_router'
ONAP_ROUTER_DESC            = 'Router created for ONAP'

EXTERNAL_NETWORK_NAME       = 'floating_net'  # OpenStack instance external network (gateway) name to be used as router's gateway

ONAP_KEYPAIR_NAME           = 'ONAP_keypair'    # keypair that can be used to SSH into created servers (VNF VMs)

# OpenStack cloud name and region name, which should be the same as in the clouds.yaml file used by this script
OPENSTACK_CLOUD_NAME        = 'hpe16openstackFraser'
OPENSTACK_REGION_NAME       = 'RegionOne'
# OpenStack domain is: Default


######################################################################
# constants which could be parameters
DNS_SERVER_IP           = '8.8.8.8'
# IP addresses of free public DNS service from Google:
# - IPv4: 8.8.8.8 and 8.8.4.4
# - IPv6: 2001:4860:4860::8888 and 2001:4860:4860::8844

######################################################################
# global variables
DEBUG_VAR = False

######################################################################
# import statements
import openstack
import argparse
import sys, traceback

######################################################################
def print_debug(*args):
    if DEBUG_VAR:
        for arg in args:
            print ('***',arg)

######################################################################
def delete_all_ONAP():
    """Delete all ONAP-specific OpenStack objects (normally not needed, but may be useful during tests)."""
    print('\nOPNFV Auto, script to delete ONAP objects in an OpenStack instance')

    try:
        # connect to OpenStack instance using Connection object from OpenStack SDK
        print('Opening connection...')
        conn = openstack.connect(
            identity_api_version    = 3,        # must indicate Identity version (until fixed); can also be in clouds.yaml
            cloud           = OPENSTACK_CLOUD_NAME,
            region_name     = OPENSTACK_REGION_NAME)

        # delete router; must delete router before networks (and must delete VMs before routers)
        print('Deleting ONAP router...')
        onap_router = conn.network.find_router(ONAP_ROUTER_NAME)
        print_debug('onap_router:',onap_router)
        if onap_router != None:
            conn.network.delete_router(onap_router.id)
        else:
            print('No ONAP router found...')


        # try:  # try to circumvent !=None issue with OpenStack Resource.py; nope;
            # onap_router = conn.network.find_router(ONAP_ROUTER_NAME)
            # print_debug('onap_router:',onap_router)
            # print_debug('onap_router.name:',onap_router.name)
            # print_debug('onap_router.id:',onap_router.id)
            # conn.network.delete_router(onap_router.id)
            # conn.network.delete_router(onap_router)
        # except Exception as e:
            # print('issue Deleting ONAP router...')
            # print('*** Exception:',type(e), e)
            # exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            # print('*** traceback.print_tb():')
            # traceback.print_tb(exceptionTraceback)
            # print('*** traceback.print_exception():')
            # traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback)


        # delete private network (which should also delete associated subnet and ports if any)
        print('Deleting ONAP private network...')
        private_network = conn.network.find_network(ONAP_PRIVATE_NET_NAME)
        print_debug('private_network:',private_network)
        if private_network != None:
            conn.network.delete_network(private_network.id)
        else:
            print('No ONAP private network found...')

        # delete OAM network (which should also delete associated subnet and ports if any)
        print('Deleting ONAP OAM network...')
        oam_network = conn.network.find_network(ONAP_OAM_NET_NAME)
        print_debug('oam_network:',oam_network)
        if oam_network != None:
            conn.network.delete_network(oam_network.id)
        else:
            print('No ONAP OAM network found...')

        # delete public network (which should also delete associated subnet and ports if any)
        print('Deleting ONAP public network...')
        public_network = conn.network.find_network(ONAP_PUBLIC_NET_NAME)
        print_debug('public_network:',public_network)
        if public_network != None:
            conn.network.delete_network(public_network.id)
        else:
            print('No ONAP public network found...')

        # delete security group
        print('Deleting ONAP security group...')
        onap_security_group = conn.network.find_security_group(ONAP_SECU_GRP_NAME)
        print_debug('onap_security_group:',onap_security_group)
        if onap_security_group != None:
            conn.network.delete_security_group(onap_security_group.id)
        else:
            print('No ONAP security group found...')

        # delete user
        print('Deleting ONAP user...')
        onap_user = conn.identity.find_user(ONAP_USER_NAME)
        print_debug('onap_user:',onap_user)
        if onap_user != None:
            conn.identity.delete_user(onap_user.id)
        else:
            print('No ONAP user found...')

        # delete project/tenant
        print('Deleting ONAP project...')
        onap_project = conn.identity.find_project(ONAP_TENANT_NAME)
        print_debug('onap_project:',onap_project)
        if onap_project != None:
            conn.identity.delete_project(onap_project.id)
        else:
            print('No ONAP project found...')

        # delete keypair
        print('Deleting ONAP keypair...')
        onap_keypair = conn.compute.find_keypair(ONAP_KEYPAIR_NAME)
        print_debug('onap_keypair:',onap_keypair)
        if onap_keypair != None:
            conn.compute.delete_keypair(onap_keypair.id)
        else:
            print('No ONAP keypair found...')


    except Exception as e:
        print('*** Exception:',type(e), e)
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print('*** traceback.print_tb():')
        traceback.print_tb(exceptionTraceback)
        print('*** traceback.print_exception():')
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback)
        print('[Script terminated]\n')

    print('OPNFV Auto, end of deletion script\n')


######################################################################
def configure_all_ONAP():
    """Configure all ONAP-specific OpenStack objects."""
    print('\nOPNFV Auto, script to configure an OpenStack instance for ONAP')

    try:
        # connect to OpenStack instance using Connection object from OpenStack SDK
        print('Opening connection...')
        conn = openstack.connect(
            identity_api_version    = 3,        # must indicate Identity version (until fixed); can also be in clouds.yaml
            cloud           = OPENSTACK_CLOUD_NAME,
            region_name     = OPENSTACK_REGION_NAME)

        ###################################################################
        # TESTS: IGNORE/DELETE (BEGIN)
        # gdserver_ID = '8bc274a2-8c0d-4795-9b4d-faa0a21e1d88'
        # gdserver = conn.compute.get_server(gdserver_ID)
        # print('\ngdserver.name=',gdserver.name)
        # print('gdserver.status=',gdserver.status)

        # print("\nList Users:")
        # i=1
        # for user in conn.identity.users():
            # print('User',str(i),user.name,'\n',user,'\n')
            # i+=1

        # print("\nList Projects:")
        # i=1
        # for project in conn.identity.projects():
            # print('Project',str(i),project.name,'\n',project,'\n')
            # i+=1

        # print("\nList Roles:")
        # i=1
        # for role in conn.identity.roles():
            # print('Role',str(i),role.name,'\n',role,'\n')
            # i+=1

        # print("\nList Networks:")
        # i=1
        # for network in conn.network.networks():
            # print('Network',str(i),network.name,'\n',network,'\n')
            # i+=1

        # print("\nList Routers:")
        # i=1
        # for router in conn.network.routers():
            # print('Router',str(i),router.name,'\n',router,'\n')
            # i+=1

        # print("\nList Flavors:")
        # i=1
        # for flvr in conn.compute.flavors():
            # print('Flavor',str(i),flvr.name,'\n',flvr,'\n')
            # i+=1

        # print("\nList Images:")
        # i=1
        # for img in conn.compute.images():
            # print('Image',str(i),img.name,'\n',img,'\n')
            # i+=1

        # router = conn.network.find_router('gd_test_router')
        # print('gd router\n',router,'\n\n')
        # router = conn.network.find_router('e4e59f63-8063-4774-a97a-c110c6969e4a')
        # print('gd router\n',router,'\n\n')
        # TESTS: IGNORE/DELETE (END)
        ###################################################################


        print('Creating ONAP project/tenant...')
        onap_project = conn.identity.find_project(ONAP_TENANT_NAME)
        if onap_project != None:
            print('ONAP project/tenant already exists')
        else:
            onap_project = conn.identity.create_project(
                name = ONAP_TENANT_NAME,
                description = ONAP_TENANT_DESC,
                is_enabled = True)
                # domain: leave default
                # project quotas (max #vCPUs, #instances, etc.): as conn.network.<*quota*>, using project id for quota id
                # https://docs.openstack.org/openstacksdk/latest/user/proxies/network.html#quota-operations
                # https://docs.openstack.org/openstacksdk/latest/user/resources/network/v2/quota.html#openstack.network.v2.quota.Quota
                # conn.network.update_quota(project_id = onap_project.id)
                # SDK for quotas supports floating_ips, networks, ports, etc. but not vCPUs or instances
        print_debug('onap_project:',onap_project)


        print('Creating ONAP user...')
        onap_user = conn.identity.find_user(ONAP_USER_NAME)
        if onap_user != None:
            print('ONAP user already exists')
        else:
            onap_user = conn.identity.create_user(
                name = ONAP_USER_NAME,
                description = ONAP_USER_DESC,
                default_project_id  = onap_project.id,
                password = ONAP_USER_PASSWORD,
                is_enabled = True)
                # domain: leave default
                # default_project_id: primary project
        print_debug('onap_user:',onap_user)

        # TODO@@@ assign Member role to ONAP user in ONAP project
        # membership_role = conn.identity.find_role('Member')
        # onap_project.assign_role_to_user(conn, onap_user, membership_role)  # no project membership method yet in connection proxy

        # TODO@@@ maybe logout and log back in as ONAP user

        # make sure security group allows ICMP (for ping) and SSH (TCP port 22) traffic; also IPv4/v6 traffic ingress and egress
        # create new onap_security_group (or maybe just "default" security group ? tests returned multiple "default" security groups)
        # security group examples: check http://git.openstack.org/cgit/openstack/openstacksdk/tree/examples/network/security_group_rules.py
        # if rule already exists, OpenStack returns an error, so just try (no harm); try each separately
        # (SecurityGroup is a Resource)
        print('Creating ONAP security group...')
        onap_security_group = conn.network.find_security_group(ONAP_SECU_GRP_NAME)
        if onap_security_group != None:
            print('ONAP security group already exists')
        else:
            onap_security_group = conn.network.create_security_group(
                #project_id  = onap_project.id,
                description = ONAP_SECU_GRP_DESC,
                name        = ONAP_SECU_GRP_NAME)
        print_debug('onap_security_group:',onap_security_group)

        try:
            description_text = 'enable ICMP ingress IPv4'
            print('  Creating rule:',description_text,'...')
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
            print('  Creating rule:',description_text,'...')
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
            print('  Creating rule:',description_text,'...')
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
            print('  Creating rule:',description_text,'...')
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
            print('  Creating rule:',description_text,'...')
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
            print('  Creating rule:',description_text,'...')
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
            # print('  Creating rule:',description_text,'...')
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
            # print('  Creating rule:',description_text,'...')
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
        print('Creating ONAP public network...')
        public_network = conn.network.find_network(ONAP_PUBLIC_NET_NAME)
        if public_network != None:
            print('ONAP public network already exists')
        else:
            public_network = conn.network.create_network(
                name = ONAP_PUBLIC_NET_NAME,
                description = ONAP_PUBLIC_NET_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True,
                is_shared = True)
                # subnet_ids = []: not needed, subnet refers to network_id
            print_debug('public_network: before subnet',public_network)

            print('  Creating subnetwork for ONAP public network...')
            public_subnet = conn.network.create_subnet(
                name = ONAP_PUBLIC_SUBNET_NAME,
                #project_id = onap_project.id,
                network_id = public_network.id,
                cidr = ONAP_PUBLIC_SUBNET_CIDR,
                ip_version = 4,
                is_dhcp_enabled = True,
                dns_nameservers = [DNS_SERVER_IP])    # list of DNS IP@
        print_debug('public_network: after subnet',public_network)
        print_debug('public_subnet:',public_subnet)


        # private network
        print('Creating ONAP private network...')
        private_network = conn.network.find_network(ONAP_PRIVATE_NET_NAME)
        if private_network != None:
            print('ONAP private network already exists')
        else:
            private_network = conn.network.create_network(
                name = ONAP_PRIVATE_NET_NAME,
                description = ONAP_PRIVATE_NET_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True,
                is_shared = True)
            print_debug('private_network: before subnet',private_network)

            print('  Creating subnetwork for ONAP private network...')
            private_subnet = conn.network.create_subnet(
                name = ONAP_PRIVATE_SUBNET_NAME,
                #project_id = onap_project.id,
                network_id = private_network.id,
                cidr = ONAP_PRIVATE_SUBNET_CIDR,
                ip_version = 4,
                is_dhcp_enabled = True,
                dns_nameservers = [DNS_SERVER_IP])    # list of DNS IP@; maybe not needed for private network
            print_debug('private_network: after subnet',private_network)
            print_debug('private_subnet:',private_subnet)


        # OAM network
        print('Creating ONAP OAM network...')
        oam_network = conn.network.find_network(ONAP_OAM_NET_NAME)
        if oam_network != None:
            print('ONAP OAM network already exists')
        else:
            oam_network = conn.network.create_network(
                name = ONAP_OAM_NET_NAME,
                description = ONAP_OAM_NET_DESC,
                #project_id = onap_project.id,
                is_admin_state_up = True,
                is_shared = True)
            print_debug('oam_network: before subnet',oam_network)

            print('  Creating subnetwork for ONAP OAM network...')
            oam_subnet = conn.network.create_subnet(
                name = ONAP_OAM_SUBNET_NAME,
                #project_id = onap_project.id,
                network_id = oam_network.id,
                cidr = ONAP_OAM_SUBNET_CIDR,
                ip_version = 4,
                is_dhcp_enabled = True,
                dns_nameservers = [DNS_SERVER_IP])    # list of DNS IP@; maybe not needed for OAM network
            print_debug('oam_network: after subnet',oam_network)
            print_debug('oam_subnet:',oam_subnet)


        # router
        print('Creating ONAP router...')
        onap_router = conn.network.find_router(ONAP_ROUTER_NAME)
        if onap_router != None:
            print('ONAP router already exists')
        else:

            # build dictionary for external network (gateway)
            external_network = conn.network.find_network(EXTERNAL_NETWORK_NAME)
            print_debug('external_network:',external_network)
            external_subnet_ID_list = external_network.subnet_ids
            print_debug('external_subnet_ID_list:',external_subnet_ID_list)
            # build external_fixed_ips: list of dictionaries, each with 'subnet_id' key (and may have 'ip_address' key as well)
            onap_gateway_external_subnets = []
            for ext_subn_id in external_subnet_ID_list:  # there should be only one subnet ID in the list, but go through each item, just in case
                onap_gateway_external_subnets.append({'subnet_id':ext_subn_id})
            print_debug('onap_gateway_external_subnets:',onap_gateway_external_subnets)
            network_dict_body = {
                'network_id': external_network.id,
                'enable_snat': True,   # True should be the default, so there should be no need to set it
                'external_fixed_ips': onap_gateway_external_subnets
            }
            print_debug('network_dict_body:',network_dict_body)

            onap_router = conn.network.create_router(
                name = ONAP_ROUTER_NAME,
                description = ONAP_ROUTER_DESC,
                #project_id = onap_project.id,
                external_gateway_info = network_dict_body,  # linking GW to router creation time (normally, could also use add_gateway_to_router)
                is_admin_state_up = True)
            print_debug('onap_router: after creation',onap_router)

            # add interfaces to ONAP networks: Public, Private, and OAM
            # syntax: add_interface_to_router(router, subnet_id=None, port_id=None)
            print('Adding interface to ONAP router for ONAP public network...')
            conn.network.add_interface_to_router(onap_router, subnet_id = public_subnet.id)
            print('Adding interface to ONAP router for ONAP private network...')
            conn.network.add_interface_to_router(onap_router, subnet_id = private_subnet.id)
            print('Adding interface to ONAP router for ONAP OAM network...')
            conn.network.add_interface_to_router(onap_router, subnet_id = oam_subnet.id)
            print_debug('onap_router: after adding interfaces',onap_router)

            # point to OpenStack external network (i.e. Gateway for router); network_id is passed in a body dictionary
            # (external network such as floating_net)
            # syntax: add_gateway_to_router(router, **body)
            #print('Adding external network (gateway) to ONAP router...')

            # nope
            # network_dict_body = {'network_id': public_network.id}
            # nope
            # network_dict_body = {
                # 'external_fixed_ips': [{'subnet_id' : public_subnet.id}],
                # 'network_id': public_network.id
            # }

            # external_network = conn.network.find_network(EXTERNAL_NETWORK_NAME)
            # print_debug('external_network:',external_network)
            # external_subnet_ID_list = external_network.subnet_ids
            # print_debug('external_subnet_ID_list:',external_subnet_ID_list)

            # # build external_fixed_ips: list of dictionaries, each with 'subnet_id' key (and may have 'ip_address' key as well)
            # onap_gateway_external_subnets = []
            # for ext_subn_id in external_subnet_ID_list:  # there should be only one subnet ID in the list, but go through each item, just in case
                # onap_gateway_external_subnets.append({'subnet_id':ext_subn_id})

            # #network_dict_body = {'gateway' : {'network_id' : external_network.id}}
            # #network_dict_body = {'network_id' : external_network.id}
            # #conn.network.add_gateway_to_router(onap_router, body=network_dict_body)
            # #conn.network.add_gateway_to_router(onap_router, network_id=external_network.id)
            # #conn.network.add_gateway_to_router(onap_router, **network_dict_body)

            # network_dict_body = {
                # 'network_id': external_network.id,
                # 'enable_snat': True,   # True should be the default, so there should be no need to set it
                # 'external_fixed_ips': onap_gateway_external_subnets
            # }
            # #conn.network.add_gateway_to_router(onap_router, **network_dict_body)
            # print_debug('onap_router: after add_gateway_to_router',onap_router)




        # # also create 5 flavors, from tiny to xlarge (hard-coded, no need for parameters)
        # # (Flavor is a Resource)
        # print('Creating flavors...')
        # print('Creating m1.tiny Flavor...')
        # tiny_flavor = conn.compute.find_flavor("m1.tiny")
        # if tiny_flavor != None:
            # print('m1.tiny Flavor already exists')
        # else:
            # tiny_flavor = conn.compute.create_flavor(
                # name = 'm1.tiny',
                # vcpus = 1,
                # disk = 1,
                # ram = 512,
                # ephemeral = 0,
                # #swap = 0,
                # #rxtx_factor = 1.0,
                # is_public = True)
        # print_debug('tiny_flavor: ',tiny_flavor)

        # print('Creating m1.small Flavor...')
        # small_flavor = conn.compute.find_flavor("m1.small")
        # if small_flavor != None:
            # print('m1.small Flavor already exists')
        # else:
            # small_flavor = conn.compute.create_flavor(
                # name = 'm1.small',
                # vcpus = 1,
                # disk = 20,
                # ram = 2048,
                # ephemeral = 0,
                # #swap = 0,
                # #rxtx_factor = 1.0,
                # is_public = True)
        # print_debug('small_flavor: ',small_flavor)

        # print('Creating m1.medium Flavor...')
        # medium_flavor = conn.compute.find_flavor("m1.medium")
        # if medium_flavor != None:
            # print('m1.medium Flavor already exists')
        # else:
            # medium_flavor = conn.compute.create_flavor(
                # name = 'm1.medium',
                # vcpus = 2,
                # disk = 40,
                # ram = 4096,
                # ephemeral = 0,
                # #swap = 0,
                # #rxtx_factor = 1.0,
                # is_public = True)
        # print_debug('medium_flavor: ',medium_flavor)

        # print('Creating m1.large Flavor...')
        # large_flavor = conn.compute.find_flavor("m1.large")
        # if large_flavor != None:
            # print('m1.large Flavor already exists')
        # else:
            # large_flavor = conn.compute.create_flavor(
                # name = 'm1.large',
                # vcpus = 4,
                # disk = 80,
                # ram = 8192,
                # ephemeral = 0,
                # #swap = 0,
                # #rxtx_factor = 1.0,
                # is_public = True)
        # print_debug('large_flavor: ',large_flavor)

        # print('Creating m1.xlarge Flavor...')
        # xlarge_flavor = conn.compute.find_flavor("m1.xlarge")
        # if xlarge_flavor != None:
            # print('m1.xlarge Flavor already exists')
        # else:
            # xlarge_flavor = conn.compute.create_flavor(
                # name = 'm1.xlarge',
                # vcpus = 8,
                # disk = 160,
                # ram = 16384,
                # ephemeral = 0,
                # #swap = 0,
                # #rxtx_factor = 1.0,
                # is_public = True)
        # print_debug('xlarge_flavor: ',xlarge_flavor)


        # create images: Ubuntu 16.04, 14.04, CirrOS, ...
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

        # do not use compute proxy for images; there is an image proxy (v1, and v2); use shade layer, directly with Connection object;
        # conn.get_image() returns a Python Munch object (subclass of Dictionary)
        # URL download not supported yet; download image separately, place it in the directory
        # https://docs.openstack.org/openstacksdk/latest/user/connection.html#openstack.connection.Connection.create_image

        IMAGE_NAME = 'CirrOS_0.4.0_minimal_Linux_distribution'
        print('Creating image:',IMAGE_NAME,'...')
        if conn.get_image(IMAGE_NAME) != None:
            print(IMAGE_NAME,'image already exists')
        else:
            conn.create_image(IMAGE_NAME, filename='cirros-0.4.0-x86_64-disk.img')

        IMAGE_NAME = 'Ubuntu_Server_16.04_LTS_Xenial_Xerus'
        print('Creating image:',IMAGE_NAME,'...')
        if conn.get_image(IMAGE_NAME) != None:
            print(IMAGE_NAME,'image already exists')
        else:
            conn.create_image(IMAGE_NAME, filename='xenial-server-cloudimg-amd64-disk1.img')

        IMAGE_NAME = 'Ubuntu_Server_14.04_LTS_Trusty_Tahr'
        print('Creating image:',IMAGE_NAME,'...')
        if conn.get_image(IMAGE_NAME) != None:
            print(IMAGE_NAME,'image already exists')
        else:
            conn.create_image(IMAGE_NAME, filename='trusty-server-cloudimg-amd64-disk1.img')


        # create a keypair, if needed e.g. for VNF VMs; maybe to SSH for testing
        # (Keypair is a Resource)
        print('Creating ONAP keypair...')
        onap_keypair = conn.compute.find_keypair(ONAP_KEYPAIR_NAME)
        if onap_keypair != None:
            print('ONAP keypair already exists')
        else:
            onap_keypair = conn.compute.create_keypair(name=ONAP_KEYPAIR_NAME)
            print('  ONAP keypair fingerprint:')
            print(onap_keypair.fingerprint)
            print('  ONAP keypair public key:')
            print(onap_keypair.public_key)
            print('  \nONAP keypair private key: (save it in a file now: it cannot be retrieved later)')
            print(onap_keypair.private_key)
        print_debug('onap_keypair:',onap_keypair)

        print('\nSUMMARY:')
        print('ONAP public network ID:',public_network.id)
        print('ONAP private network ID:',private_network.id)
        print('ONAP private network subnet ID:',private_subnet.id)
        print('ONAP private network subnet CIDR:',private_subnet.cidr)
        print('\n')

    except Exception as e:
        print('*** Exception:',type(e), e)
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print('*** traceback.print_tb():')
        traceback.print_tb(exceptionTraceback)
        print('*** traceback.print_exception():')
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback)
        print('[Script terminated]\n')


    print('OPNFV Auto, end of configuration script\n')



######################################################################
def main():

    # configure argument parser: 2 optional arguments
    # "-del" or "--delete" option to delete ONAP configuration in OpenStack
    #   (if no "-del" or "--delete", then configure OpenStack for ONAP
    # "-deb" or "--debug" option to display debug information
    parser = argparse.ArgumentParser()
    parser.add_argument('-deb', '--debug',
        help   = 'display debug information during execution',
        action = 'store_true')
    parser.add_argument('-del', '--delete',
        help   = 'delete ONAP configuration',
        action = 'store_true')

    # parse arguments, modify global variable if need be, and use corresponding script
    args = parser.parse_args()
    if args.debug:
        global DEBUG_VAR
        DEBUG_VAR = True
    if args.delete:
        delete_all_ONAP()
    else:
        configure_all_ONAP()


if __name__ == "__main__":
    main()

