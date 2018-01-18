#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

"""Module to manage OpenStack"""

import os
import re
import sys
import time
import traceback

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient import client as keystoneclient
from glanceclient import client as glanceclient
from neutronclient.neutron import client as neutronclient
from novaclient import client as novaclient
from heatclient import client as heatclient

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"

DEFAULT_API_VERSION = '2'

openrc_base_key = ['OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD']

openrc_v3_exkey = ['OS_PROJECT_NAME',
                   'OS_USER_DOMAIN_NAME',
                   'OS_PROJECT_DOMAIN_NAME']

openrc_v2_exkey = ['OS_TENANT_NAME']

openrc_vars_mapping = {
        'OS_USERNAME': 'username',
        'OS_PASSWORD': 'password',
        'OS_AUTH_URL': 'auth_url',
        'OS_TENANT_NAME': 'tenant_name',
        'OS_USER_DOMAIN_NAME': 'user_domain_name',
        'OS_PROJECT_DOMAIN_NAME': 'project_domain_name',
        'OS_PROJECT_NAME': 'project_name',
    }


def check_identity_api_version():
    identity_api_version = os.getenv('OS_IDENTITY_API_VERSION')
    auth_url = os.getenv('OS_AUTH_URL')
    if not auth_url:
        raise RuntimeError("Require env var: OS_AUTH_URL")
    auth_url_parse = auth_url.split('/')
    url_tail = auth_url_parse[-1] if auth_url_parse[-1] else auth_url_parse[-2]
    url_identity_version = url_tail.strip('v')
    if not identity_api_version and \
           identity_api_version != url_identity_version:
        raise RuntimeError("identity api version not consistent")
    return url_identity_version


def check_image_api_version():
    image_api_version = os.getenv('OS_IMAGE_API_VERSION')
    if image_api_version:
        return image_api_version
    else:
        return DEFAULT_API_VERSION


def check_network_api_version():
    network_api_version = os.getenv('OS_NETWORK_API_VERSION')
    if network_api_version:
        return network_api_version
    else:
        return DEFAULT_API_VERSION


def check_compute_api_version():
    compute_api_version = os.getenv('OS_COMPUTE_API_VERSION')
    if compute_api_version:
        return compute_api_version
    else:
        return DEFAULT_API_VERSION


def get_project_name(creds):
    identity_version = check_identity_api_version()
    if identity_version == '3':
        return creds["project_name"]
    elif identity_version == '2':
        return creds["tenant_name"]
    else:
        raise RuntimeError("Unsupported identity version")


def get_credentials():
    creds = {}
    creds_env_key = openrc_base_key
    identity_api_version = check_identity_api_version()

    if identity_api_version == '3':
        creds_env_key += openrc_v3_exkey
    elif identity_api_version == '2':
        creds_env_key += openrc_v2_exkey
    else:
        raise RuntimeError("Unsupported identity version")

    for env_key in creds_env_key:
        env_value = os.getenv(env_key)
        if env_value is None:
            raise RuntimeError("Require env var: %s" % env_key)
        else:
            creds_var = openrc_vars_mapping.get(env_key)
            creds.update({creds_var: env_value})

    return creds


def get_session_auth(creds):
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(**creds)
    return auth


def get_session(creds):
    auth = get_session_auth(creds)
    cacert = os.getenv('OS_CACERT')
    insecure = os.getenv('OS_INSECURE', '').lower() == 'true'
    verify = cacert if cacert else not insecure
    return session.Session(auth=auth, verify=verify)


def get_keystone_client(creds):
    identity_api_version = check_identity_api_version()
    sess = get_session(creds)
    return keystoneclient.Client(identity_api_version,
                                 session=sess,
                                 interface=os.getenv('OS_INTERFACE', 'admin'))


def get_glance_client(creds):
    image_api_version = check_image_api_version()
    sess = get_session(creds)
    return glanceclient.Client(image_api_version, session=sess)


def get_neutron_client(creds):
    network_api_version = check_network_api_version()
    sess = get_session(creds)
    return neutronclient.Client(network_api_version, session=sess)


def get_nova_client(creds):
    compute_api_version = check_compute_api_version()
    sess = get_session(creds)
    return novaclient.Client(compute_api_version, session=sess)


def get_domain_id(keystone_client, domain_name):
    domains = keystone_client.domains.list()
    domain_id = None
    for domain in domains:
        if domain.name == domain_name:
            domain_id = domain.id
            break
    return domain_id


def get_project_id(keystone_client, project_name):
    identity_version = check_identity_api_version()
    if identity_version == '3':
        projects = keystone_client.projects.list()
    elif identity_version == '2':
        projects = keystone_client.tenants.list()
    else:
        raise RuntimeError("Unsupported identity version")
    project_id = None
    for project in projects:
        if project.name == project_name:
            project_id = project.id
            break
    return project_id


def get_image_id(glance_client, image_name):
    images = glance_client.images.list()
    image_id = None
    for image in images:
        if image.name == image_name:
            image_id = image.id
            break
    return image_id


def get_security_group_id(neutron_client, secgroup_name, project_id=None):
    security_groups = neutron_client.list_security_groups()['security_groups']
    secgroup_id = []
    for security_group in security_groups:
        if security_group['name'] == secgroup_name:
            secgroup_id = security_group['id']
            if security_group['project_id'] == project_id or project_id is None:
                break
    return secgroup_id


def get_secgroup_rule_id(neutron_client, secgroup_id, json_body):
    secgroup_rules = \
        neutron_client.list_security_group_rules()['security_group_rules']
    secgroup_rule_id = None
    for secgroup_rule in secgroup_rules:
        rule_match = True
        for key, value in json_body['security_group_rule'].items():
            rule_match = rule_match and (value == secgroup_rule[key])
        if rule_match:
            secgroup_rule_id = secgroup_rule['id']
            break
    return secgroup_rule_id


def get_keypair_id(nova_client, keypair_name):
    keypairs = nova_client.keypairs.list()
    keypair_id = None
    for keypair in keypairs:
        if keypair.name == keypair_name:
            keypair_id = keypair.id
            break
    return keypair_id


def create_project(keystone_client, creds, project_name, project_desc):
    project_id = get_project_id(keystone_client, project_name)
    if project_id:
        return project_id

    identity_version = check_identity_api_version()

    if identity_version == '3':
        domain_name = creds["user_domain_name"]
        domain_id = get_domain_id(keystone_client, domain_name)
        project = keystone_client.projects.create(
                    name=project_name,
                    description=project_desc,
                    domain=domain_id,
                    enabled=True)
    elif identity_version == '2':
        project = keystone_client.tenants.create(project_name,
                                                 project_desc,
                                                 enabled=True)
    else:
        raise RuntimeError("Unsupported identity version")

    return project.id


def create_image(glance_client, image_name, image_path, disk_format="qcow2",
                 container_format="bare", visibility="public"):
    if not os.path.isfile(image_path):
        raise RuntimeError("Image file not found: %s" % image_path)
    image_id = get_image_id(glance_client, image_name)
    if not image_id:
        image = glance_client.images.create(name=image_name,
                                            visibility=visibility,
                                            disk_format=disk_format,
                                            container_format=container_format)
        image_id = image.id
        with open(image_path) as image_data:
            glance_client.images.upload(image_id, image_data)
    return image_id


def create_secgroup_rule(neutron_client, secgroup_id, protocol, direction,
                         port_range_min=None, port_range_max=None):
    json_body = {'security_group_rule': {'direction': direction,
                                         'security_group_id': secgroup_id,
                                         'protocol': protocol}}

    if bool(port_range_min) != bool(port_range_max):
        raise RuntimeError("Start or end of protocol range is empty: [ %s, %s ]"
                            % (port_range_min, port_range_max))
    elif port_range_min and port_range_max:
        json_body['security_group_rule'].update({'port_range_min':
                                                port_range_min})
        json_body['security_group_rule'].update({'port_range_max':
                                                         port_range_max})

    secgroup_id = get_secgroup_rule_id(neutron_client, secgroup_id, json_body)
    if not secgroup_id:
        neutron_client.create_security_group_rule(json_body)
    return secgroup_id


def update_compute_quota(nova_client, project_id, quotas):
    nova_client.quotas.update(project_id, **quotas)


def create_keypair(nova_client, keypair_name, keypair_path):
    keypair_id = get_keypair_id(nova_client, keypair_name)
    if not keypair_id:
        with open(os.path.expanduser(keypair_path), 'r') as public_key:
            key_data = public_key.read().decode('utf-8')
            keypair = nova_client.keypairs.create(name=keypair_name,
                                                  public_key=key_data)
        keypair_id = keypair.id
    return keypair_id

