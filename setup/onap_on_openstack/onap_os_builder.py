#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

"""ONAP builder for OpenStack"""

import os
import sys

import auto.util.openstack_lib as os_lib
import auto.util.util as util
from auto.util.yaml_type import literal_unicode

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


class ONAP_os_builder(object):
    """Prepare the OpenStack environment and launch ONAP stack"""
    def __init__(self, config_file):

        self.config = util.read_yaml(config_file)
        self.stack_name = self.config['onap_stack_name']
        self.demo_git = self.config['onap_demo_git']
        self.vm_images = self.config['onap_vm_images']
        self.secgroup_rules = self.config['onap_secgroup_rules']
        self.quota = self.config['onap_quota']
        self.keypair = self.config['onap_keypair']
        self.user_config = self.config['onap_user_config']

        self.creds = os_lib.get_credentials()
        self.keystone_client = os_lib.get_keystone_client(self.creds)
        self.glance_client = os_lib.get_glance_client(self.creds)
        self.neutron_client = os_lib.get_neutron_client(self.creds)
        self.nova_client = os_lib.get_nova_client(self.creds)
        self.heat_client = os_lib.get_heat_client(self.creds)

        self.auto_dir = os.getenv('AUTO_DIR')
        self.work_dir = os.path.join(self.auto_dir, "work")
        self.demo_repo_dir = os.path.join(self.work_dir, "demo")
        self.heat_template = os.path.join(self.demo_repo_dir,
                                          self.demo_git['heat_template'])
        self.heat_env = os.path.join(self.demo_repo_dir,
                                     self.demo_git['heat_env'])
        self.image_dir = os.path.join(self.work_dir, "images")
        self.keypair_dir = os.path.join(self.work_dir, "keypair")
        util.mkdir(self.work_dir)


    def clone_demo_code(self):
        util.git_clone(self.demo_git['repo'], self.demo_git['branch'],
                       self.demo_repo_dir)


    def prepare_images(self):
        util.mkdir(self.image_dir)
        for _, image_info in self.vm_images.items():
            image_path = os.path.join(self.image_dir, image_info['name'])
            util.download(image_info['url'], image_path)


    def create_onap_vm_images(self):
        self.prepare_images()
        for _, image_info in self.vm_images.items():
            image_path = os.path.join(self.image_dir, image_info['name'])
            os_lib.create_image(self.glance_client,
                                image_info['name'],
                                image_path)


    def create_onap_secgroup_rules(self):
        project_name = os_lib.get_project_name(self.creds)
        project_id = os_lib.get_project_id(self.keystone_client, project_name)
        secgroup_id = os_lib.get_security_group_id(self.neutron_client,
                                                   "default", project_id)
        for secgroup_rule in self.secgroup_rules:
            os_lib.create_secgroup_rule(self.neutron_client, secgroup_id,
                                        secgroup_rule['protocol'],
                                        secgroup_rule['direction'],
                                        secgroup_rule['port_range_min'],
                                        secgroup_rule['port_range_max'])


    def set_quota(self):
        project_name = os_lib.get_project_name(self.creds)
        project_id = os_lib.get_project_id(self.keystone_client, project_name)
        os_lib.update_compute_quota(self.nova_client, project_id, self.quota)


    def create_onap_key(self):
        os_lib.create_keypair(self.nova_client, self.keypair['name'],
                              self.keypair['pubkey_path'])


    def set_onap_stack_params(self):
        stack_config = util.read_yaml(self.heat_env)['parameters']

        user_config = self.user_config
        user_config.update({'ubuntu_1404_image':
                      self.vm_images['ubuntu_1404_image']['name']})
        user_config.update({'ubuntu_1604_image':
                      self.vm_images['ubuntu_1604_image']['name']})
        user_config.update({'dcae_centos_7_image':
                      self.vm_images['dcae_centos_7_image']['name']})

        pubkey_data = util.read_file(self.keypair['pubkey_path']).strip('\n')
        user_config.update({'key_name': self.keypair['name']})
        user_config.update({'pub_key': literal_unicode(pubkey_data)})

        util.mkdir(self.keypair_dir)
        prikey_path = os.path.join(self.keypair_dir, 'private.key')
        pubkey_path = os.path.join(self.keypair_dir, 'public.key')
        if not os.path.isfile(prikey_path) or not os.path.isfile(pubkey_path):
            util.create_keypair(prikey_path, pubkey_path)

        dcae_prikey_data = util.read_file(prikey_path).strip('\n')
        dcae_pubkey_data = util.read_file(pubkey_path).strip('\n')
        user_config.update({'dcae_public_key':
                            literal_unicode(dcae_pubkey_data)})
        user_config.update({'dcae_private_key':
                            literal_unicode(dcae_prikey_data)})

        public_net_id = os_lib.get_network_id(
            self.neutron_client,
            user_config['public_net_name']
        )
        user_config.update({'public_net_id': public_net_id})
        project_id = os_lib.get_project_id(
            self.keystone_client,
            user_config['openstack_tenant_name']
        )
        user_config.update({'openstack_tenant_id': project_id})

        for key, value in user_config.items():
            stack_config[key] = value
        heat_env_data = {'parameters': stack_config}
        util.write_yaml(heat_env_data, self.heat_env)


    def create_onap_stack(self):
        stack_args = {}
        stack_args['stack_name'] = self.stack_name
        stack_args['template'] = util.read_file(self.heat_template)
        stack_args['parameters'] = util.read_yaml(self.heat_env)['parameters']
        self.heat_client.stacks.create(**stack_args)

