#!/usr/bin/env python3

# ===============LICENSE_START=======================================================
# Apache-2.0
# ===================================================================================
# Copyright (C) 2018 Wipro. All rights reserved.
# ===================================================================================
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================


# OPNFV Auto project
# https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095

# Use case 02: Resilience Improvements
# Use Case description: https://wiki.opnfv.org/display/AUTO/Auto+Use+Cases
# Test case design: https://wiki.opnfv.org/display/AUTO/Use+case+2+%28Resilience+Improvements+through+ONAP%29+analysis

# This module: execution of tests
# (might merge this module with Main module)
## Receive/retrieve chosen test def info
##pre-test (pings, etc.)
##launch test:
##  create execution instances of Test and Challenge
##  simulate challenge
##  get time T1
##  loop:
##    wait for VNF recovery
##    optional other metrics
##    store data and logs
##  get time T2
##  stop challenge
##  reset (with ONAP MSO)
##  store data and logs
##post-tests
##logs



def f1():
    return 0




