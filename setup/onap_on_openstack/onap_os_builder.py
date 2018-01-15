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
import constants as CONST
import util.openstack_lib as os_lib
import util.util as util

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


class ONAP_os_builder(object):
    """Prepare the OpenStack environment and launch ONAP stack"""
    def __init__(self):
        self.tenant_name = CONST.ONAP_TENANT_NAME
        self.vm_images = CONST.ONAP_VM_IMAGES
        self.security_rule = CONST.ONAP_SECURITY_RULE
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
        for image_name, image_url in self.vm_images.items():
            image_path = os.path.join(self.image_dir, image_name)
            util.download(image_url, image_path)


    def create_onap_tenant(self):
        os_lib.create_tenant(self.keystone_client,
                              self.creds,
                              self.tenant_name,
                              "ONAP tenant")


    def create_onap_vm_images(self):
        self.parepare_images()
        for image_name in self.vm_images:
            image_path = os.path.join(self.image_dir, image_name)
            os_lib.create_image(self.glance_client, image_name, image_path)


    def create_onap_secgroup_rules(self):
        tenant_name = os_lib.get_tenant_name(self.creds)
        tenant_id = os_lib.get_tenant_id(self.keystone_client, tenant_name)
        secgroup_id = os_lib.get_security_group_id(self.neutron_client,
                                                   "default", tenant_id)
        os_lib.create_secgroup_rule(self.neutron_client, secgroup_id,
                                    self.security_rule['protocol'],
                                    self.security_rule['direction'],
                                    self.security_rule['port_range_min'],
                                    self.security_rule['port_range_max'])


    def set_proper_quota(self):
        pass


    def create_onap_stack(self):
        pass
