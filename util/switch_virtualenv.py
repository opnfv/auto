#!/usr/bin/env python
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

"""Switch to virtualenv"""

import os
import site

__author__ = "Harry Huang <huangxiangyu5@huawei.com>"

home_dir = os.path.expanduser('~')
venv_dir = '%s/.virtualenvs/auto' % home_dir
activate_this = '%s/bin/activate_this.py' % venv_dir
execfile(activate_this, dict(__file__=activate_this))
site.addsitedir('%s/lib/python2.7/site-packages' % venv_dir)
