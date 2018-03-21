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

# for method 1 and 2
#import openstack

#for method 3
from openstack import connection

def os_list_servers(conn):
    """List OpenStack servers."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/compute.html
    if conn != None:
        print("\nList Servers:")

        try:
            i=1
            for server in conn.compute.servers():
                print('Server',str(i),'\n',server,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Servers\n")


def os_list_networks(conn):
    """List OpenStack networks."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/network.html
    if conn != None:
        print("\nList Networks:")

        try:
            i=1
            for network in conn.network.networks():
                print('Network',str(i),'\n',network,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Networks\n")


def os_list_volumes(conn):
    """List OpenStack volumes."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/proxies/block_storage.html
    # note: The block_storage member will only be added if the service is detected.
    if conn != None:
        print("\nList Volumes:")

        try:
            i=1
            for volume in conn.block_storage.volumes():
                print('Volume',str(i),'\n',volume,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Volumes\n")

            
def os_list_users(conn):
    """List OpenStack users."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Users:")

        try:
            i=1
            for user in conn.identity.users():
                print('User',str(i),'\n',user,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Users\n")
            
def os_list_projects(conn):
    """List OpenStack projects."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Projects:")

        try:
            i=1
            for project in conn.identity.projects():
                print('Project',str(i),'\n',project,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Projects\n")
            

def os_list_domains(conn):
    """List OpenStack domains."""
    # see https://docs.openstack.org/python-openstacksdk/latest/user/guides/identity.html
    if conn != None:
        print("\nList Domains:")

        try:
            i=1
            for domain in conn.identity.domains():
                print('Domain',str(i),'\n',domain,'n')
                i+=1
        except Exception as e:
            print("Exception:",type(e), e)
            print("No Domains\n")




        
        

def gdtest_openstack():
    # Method 1: assume there is a clouds.yaml file in PATH, starting path search with local directory
    #conn = openstack.connect(cloud='armopenstack', region_name='RegionOne')
    #conn = openstack.connect(cloud='hpe16openstack', region_name='RegionOne')
    # getting error: AttributeError: module 'openstack' has no attribute 'connect'

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
    # getting error: AttributeError: module 'openstack' has no attribute 'connect'

    # Method 3: create Connection object directly
    auth_args = {
        #'auth_url': 'https://10.10.50.103:5000/v2.0',  # Arm
        #'auth_url': 'http://10.16.0.101:5000/v2.0',  # hpe16, Euphrates
        'auth_url': 'http://10.16.0.107:5000/v3',  # hpe16, Fraser
        'project_name': 'admin',
        'username': 'admin',
        'password': 'opnfv_secret',
        'region_name': 'RegionOne', 
        'domain': 'Default'}
    conn = connection.Connection(**auth_args)

    #conn = connection.Connection(
        #auth_url='http://10.16.0.107:5000/v3',
        #project_name='admin',
        #username='admin',
        #password='opnfv_secret')


    os_list_servers(conn)
    os_list_networks(conn)
    os_list_volumes(conn)
    os_list_users(conn)
    os_list_projects(conn)
    os_list_domains(conn)


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

    print("Ciao\n")

if __name__ == "__main__":
    main()


# OpenStack HTTP API: https://developer.openstack.org/api-ref/compute/
#{your_compute_service_url}/servers/{server_id}/action
#GET
#http://mycompute.pvt/compute/v2.1/servers/{server_id}/suspend
#http://mycompute.pvt/compute/v2.1/servers/{server_id}/resume
# but better use the python unified client


