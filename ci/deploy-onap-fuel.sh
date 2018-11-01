#!/bin/bash
#
# Copyright 2018 Tieto
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script for automated deployment of ONAP on top of OPNFV Fuel/MCP installation
# In the future both OOM and heat install methods should be supported.
# At the beginning OOM will be used for simplification.

# Download VM images

# Import images into Glance

# Create xlarge flavor

# Deploy two VMs with enough RAM and cpus

# Run Richard's ci/deploy-onap.sh, which uses OOM for ONAP deployment

# TODO:
#   Configure ONAP to be able to control underlying OpenStack
#   Implement support for ONAP configuration, i.e. ONAP component selection
#   for installation
