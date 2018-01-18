#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

import os
from setuptools import setup, find_packages

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"


requirement_path = os.path.join(
    os.path.dirname(__file__), 'requirements.txt')
with open(requirement_path, 'r') as fd:
    requirements = [line.strip() for line in fd if line != '\n']

setup(
    name="auto",
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements
)
