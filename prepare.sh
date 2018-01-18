#!/bin/bash
########################################################################
# Copyright (c) 2018 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
########################################################################

pip install virtualenv
virtualenv venv
pip install setuptools
AUTO_DIR=$(pwd)
cat << EOF >> venv/bin/activate
export AUTO_DIR=$AUTO_DIR
EOF
python setup.py install
