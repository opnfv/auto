#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

"""Utility Module"""

import os
import urllib
import yaml
import traceback
from Crypto.PublicKey import RSA
from yaml_type import literal_unicode

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


def unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
    return node


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        return True
    else:
        return False


def download(url, file_path):
    if os.path.exists(file_path):
        return False
    else:
        urllib.urlretrieve(url, file_path)
        return True

def read_file(file_path):
    with open(os.path.expanduser(file_path)) as fd:
        return fd.read()


def read_yaml(yaml_path):
    with open(os.path.expanduser(yaml_path)) as fd:
        return yaml.safe_load(fd)


def write_yaml(yaml_data, yaml_path, default_style=False):
    yaml.add_representer(literal_unicode, literal_unicode_representer)
    yaml.add_representer(unicode, unicode_representer)
    with open(os.path.expanduser(yaml_path), 'w') as fd:
        return yaml.dump(yaml_data, fd,
                         default_flow_style=default_style)


def create_keypair(prikey_path, pubkey_path, size=2048):
    key = RSA.generate(size)
    with open(os.path.expanduser(prikey_path), 'w') as prikey_file:
        os.chmod(prikey_path, 0600)
        prikey_file.write(key.exportKey('PEM'))
    pubkey = key.publickey()
    with open(os.path.expanduser(pubkey_path), 'w') as pubkey_file:
        pubkey_file.write(pubkey.exportKey('OpenSSH'))
