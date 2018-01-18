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

sys.path.append('../../')
import config as CONFIG
import util.switch_virtualenv
import util.openstack_lib as os_lib
import util.util as util

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


class ONAP_os_builder(object):
    """Prepare the OpenStack environment and launch ONAP stack"""
    def __init__(self, heat_template, heat_env):
        self.heat_template = heat_template
        self.heat_env = heat_env

        self.project_name = CONFIG.ONAP_PROJECT_NAME
        self.vm_images = CONFIG.ONAP_VM_IMAGES
        self.secgroup_rules = CONFIG.ONAP_SECURITY_RULES
        self.quota = CONFIG.ONAP_QUOTA
        self.keypair = CONFIG.ONAP_KEYPAIR
        self.stack_config = CONFIG.ONAP_STACK_CONFIG

        self.creds = os_lib.get_credentials()
        self.keystone_client = os_lib.get_keystone_client(self.creds)
        self.glance_client = os_lib.get_glance_client(self.creds)
        self.neutron_client = os_lib.get_neutron_client(self.creds)
        self.nova_client = os_lib.get_nova_client(self.creds)
        self.work_dir = "../../work"
        self.image_dir = os.path.join(self.work_dir, "images")
        util.mkdir(self.work_dir)


    def parepare_images(self):
        util.mkdir(self.image_dir)
        for _, image_info in self.vm_images.items():
            image_path = os.path.join(self.image_dir, image_info['name'])
            util.download(image_info['url'], image_path)


    def create_onap_project(self):
        os_lib.create_project(self.keystone_client,
                              self.creds,
                              self.project_name,
                              "ONAP tenant")


    def create_onap_vm_images(self):
        self.parepare_images()
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
                              self.keypair['path'])


    def set_onap_stack_params(self):
        env_data = util.yaml_load(self.heat_env)
        

    def create_onap_stack(self):
        pass

