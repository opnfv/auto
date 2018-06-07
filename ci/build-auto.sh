#!/bin/bash
#
# Copyright 2015-2018 Intel Corporation., Tieto
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

# CI helper script for execution of AUTO project jenkins jobs.
# This script is based on the file ci/build-vsperf.sh from OPNFV vswitchperf
# project.

# Usage:
#       build-auto.sh job_type
#   where job_type is one of "verify", "merge", "daily"
#
# Example:
#       ./ci/build-auto.sh daily

#
# exit codes
#
EXIT=0
EXIT_UNKNOWN_JOB_TYPE=1

#
# configuration
#
AUTOENV_DIR="$HOME/autoenv"

#
# main
#
echo

# enter workspace dir
cd $WORKSPACE

# create virtualenv if needed
if [ ! -e $AUTOENV_DIR ] ; then
    echo "Create AUTO environment"
    echo "======================="
    virtualenv "$AUTOENV_DIR"
    echo
fi

# activate and update virtualenv
echo "Update AUTO environment"
echo "======================="
source "$AUTOENV_DIR"/bin/activate
pip install -r ./requirements.txt
echo

# execute job based on passed parameter
case $1 in
    "verify")
        echo "==============="
        echo "AUTO verify job"
        echo "==============="

        # Example of verify job body. Functions can call
        # external scripts, etc.

        #execute_auto_pylint_check
        #execute_auto_doc_check
        #install_opnfv MCP
        #install_onap
        #execute_sanity_check
        #execute_tests $1

        # Everything went well, so report SUCCESS to Jenkins
        exit $EXIT
        ;;
    "merge")
        echo "=============="
        echo "AUTO merge job"
        echo "=============="

        # Example of merge job body. Functions can call
        # external scripts, etc.

        #execute_auto_pylint_check
        #execute_auto_doc_check
        #install_opnfv MCP
        #install_onap
        #execute_sanity_check
        #execute_tests $1

        # Everything went well, so report SUCCESS to Jenkins
        exit $EXIT
        ;;
    "daily")
        echo "=============="
        echo "AUTO daily job"
        echo "=============="

        # Example of daily job body. Functions can call
        # external scripts, etc.

        #install_opnfv MCP
        #install_onap
        #execute_sanity_check
        #execute_tests $1
        #push_results_and_logs_to_artifactory

        # Everything went well, so report SUCCESS to Jenkins
        exit $EXIT
        ;;
    *)
        echo
        echo "ERRROR: Unknown job type \"$1\""
        echo
        exit $EXIT_UNKNOWN_JOB_TYPE
        ;;
esac

exit $EXIT_UNKNOWN_JOB_TYPE

#
# end
#
