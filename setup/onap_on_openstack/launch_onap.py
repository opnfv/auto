#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

"""Launch ONAP on OpenStack"""

import argparse
from onap_os_builder import ONAP_os_builder

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


def read_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
                        dest = 'config',
                        action = 'store',
                        default = './config.yml',
                        help = 'config file')
    return parser.parse_args()


if __name__ == '__main__':
    args = read_cli_args()
    config = args.config
    onap_builder = ONAP_os_builder(config)
    onap_builder.clone_demo_code()
    onap_builder.create_onap_vm_images()
    onap_builder.create_onap_secgroup_rules()
    onap_builder.set_quota()
    onap_builder.create_onap_key()
    onap_builder.set_onap_stack_params()
    onap_builder.create_onap_stack()
