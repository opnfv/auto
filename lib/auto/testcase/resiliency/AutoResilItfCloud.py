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

# Use case 02: Resilience Improvements
# Use Case description: https://wiki.opnfv.org/display/AUTO/Auto+Use+Cases
# Test case design: https://wiki.opnfv.org/display/AUTO/Use+case+2+%28Resilience+Improvements+through+ONAP%29+analysis

# This module: interfaces with cloud managers (OpenStack, Kubernetes, AWS, ...)


######################################################################
# import statements
import AutoResilGlobal
import time

# for method 1 and 2
import openstack

#for method 3
#from openstack import connection

def openstack_list_servers(conn):
    """List OpenStack servers."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/compute.html
    if conn != None:
        print("\nList Servers:")

        try:
            i=1
            for server in conn.compute.servers():
                print('Server',str(i))
                print('  Name:',server.name)
                print('  ID:',server.id)
                print('  key:',server.key_name)
                print('  status:',server.status)
                print('  AZ:',server.availability_zone)
                print('Details:\n',server)
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Servers\n")


def openstack_list_networks(conn):
    """List OpenStack networks."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/network.html
    if conn != None:
        print("\nList Networks:")

        try:
            i=1
            for network in conn.network.networks():
                print('Network',str(i),'\n',network,'\n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Networks\n")


def openstack_list_volumes(conn):
    """List OpenStack volumes."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/block_storage.html
    # note: The block_storage member will only be added if the service is detected.
    if conn != None:
        print("\nList Volumes:")

        try:
            i=1
            for volume in conn.block_storage.volumes():
                print('Volume',str(i))
                print('  Name:',volume.name)
                print('  ID:',volume.id)
                print('  size:',volume.size)
                print('  status:',volume.status)
                print('  AZ:',volume.availability_zone)
                print('Details:\n',volume)
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Volumes\n")


def openstack_list_users(conn):
    """List OpenStack users."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Users:")

        try:
            i=1
            for user in conn.identity.users():
                print('User',str(i),'\n',user,'\n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Users\n")

def openstack_list_projects(conn):
    """List OpenStack projects."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Projects:")

        try:
            i=1
            for project in conn.identity.projects():
                print('Project',str(i),'\n',project,'\n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Projects\n")


def openstack_list_domains(conn):
    """List OpenStack domains."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Domains:")

        try:
            i=1
            for domain in conn.identity.domains():
                print('Domain',str(i),'\n',domain,'\n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Domains\n")







def gdtest_openstack():

    # Method 1 (preferred) : assume there is a clouds.yaml file in PATH, starting path search with local directory
    #conn = openstack.connect(cloud='armopenstack', region_name='RegionOne')
    #conn = openstack.connect(cloud='hpe16openstackEuphrates', region_name='RegionOne')
    #conn = openstack.connect(cloud='hpe16openstackFraser', region_name='RegionOne')
    conn = openstack.connect(cloud='unh-hpe-openstack-fraser', region_name='RegionOne')
    # if getting error: AttributeError: module 'openstack' has no attribute 'connect', check that openstack is installed for this python version


    # Method 2: pass arguments directly, all as strings
    # see details at https://docs.openstack.org/python-openstacksdk/latest/user/connection.html
    # conn = openstack.connect(
        # auth_url='https://10.10.50.103:5000/v2.0',
        # project_name='admin',
        # username='admin',
        # password='opnfv_secret',
        # region_name='RegionOne',
        # )
    # conn = openstack.connect(
        # auth_url='http://10.16.0.101:5000/v2.0',
        # project_name='admin',
        # username='admin',
        # password='opnfv_secret',
        # region_name='RegionOne',
        # )
    # if getting error: AttributeError: module 'openstack' has no attribute 'connect', check that openstack is installed for this python version


    # Method 3: create Connection object directly
    # auth_args = {
        # #'auth_url': 'https://10.10.50.103:5000/v2.0',  # Arm
        # #'auth_url': 'http://10.16.0.101:5000/v2.0',  # hpe16, Euphrates
        # 'auth_url': 'http://10.16.0.107:5000/v3',  # hpe16, Fraser
        # 'project_name': 'admin',
        # 'username': 'admin',
        # 'password': 'opnfv_secret',
        # 'region_name': 'RegionOne',
        # 'domain': 'Default'}
    # conn = connection.Connection(**auth_args)

    #conn = connection.Connection(
        #auth_url='http://10.16.0.107:5000/v3',
        #project_name='admin',
        #username='admin',
        #password='opnfv_secret')


    openstack_list_servers(conn)
    openstack_list_networks(conn)
    openstack_list_volumes(conn)
    openstack_list_users(conn)
    openstack_list_projects(conn)
    openstack_list_domains(conn)

    # VM test: create a test VM in the OpenStack instance, enter its ID here
    gds_ID = '5d07da11-0e85-4256-9894-482dcee4a5f0'
    gds = conn.compute.get_server(gds_ID)
    print('\ngds.name=',gds.name)
    print('gds.status=',gds.status)
    print('suspending...')
    conn.compute.suspend_server(gds_ID)  # NOT synchronous: returns before suspension action is completed
    wait_seconds = 10
    print('  waiting',wait_seconds,'seconds...')
    time.sleep(wait_seconds)
    gds = conn.compute.get_server(gds_ID)  # need to refresh data; not maintained live
    print('gds.status=',gds.status)
    print('resuming...')
    conn.compute.resume_server(gds_ID)
    print('  waiting',wait_seconds,'seconds...')
    time.sleep(wait_seconds)
    gds = conn.compute.get_server(gds_ID)  # need to refresh data; not maintained live
    print('gds.status=',gds.status)



    #Volume test: volume attached to test VM; get its ID and enter it here
    gdv_ID = 'd0206ff2-507c-444a-9871-b5b7ea704994'
    gdv = conn.block_storage.get_volume(gdv_ID)
    # no API for stopping/restarting a volume... only delete. ONAP would have to completely migrate a VNF depending on this volume
    print('\ngdv.name=',gdv.name)
    print('gdv.status=',gdv.status)
    #gdv_recreate = gdv
    #print('deleting...')
    #conn.block_storage.delete_volume(gdv_ID)
    #conn.block_storage.delete_volume(gdv)
    #print('recreating...')
    #gdv = conn.block_storage.create_volume(<attributes saved in gdv_recreate>)


    # get_server(server): Get a single Server
    # Parameters:    server – The value can be the ID of a server or a Server instance.
    # conn.compute.get_server(server)

    # suspend_server(server): Suspends a server and changes its status to SUSPENDED.
    # Parameters:    server – Either the ID of a server or a Server instance.
    # conn.compute.suspend_server(server)

    # resume_server(server): Resumes a suspended server and changes its status to ACTIVE.
    # Parameters:    server – Either the ID of a server or a Server instance.
    # conn.compute.resume_server(server)


def main():

    print("\nTest Auto Cloud Interface")

    gdtest_openstack()

    print("\nCiao\n")

if __name__ == "__main__":
    main()


# OpenStack HTTP API: https://developer.openstack.org/api-ref/compute/
#{your_compute_service_url}/servers/{server_id}/action
#GET
#http://mycompute.pvt/compute/v2.1/servers/{server_id}/suspend
#http://mycompute.pvt/compute/v2.1/servers/{server_id}/resume
# but better use the python unified client


