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

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"

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
