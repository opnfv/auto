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
#
# Parameters:
#       job_type - is one of "verify", "merge" or "daily"
#
# Example:
#       ./ci/build-auto.sh verify

#
# exit codes
#
EXIT=0
EXIT_UNKNOWN_JOB_TYPE=1
EXIT_LINT_FAILED=2

#
# configuration
#
AUTOENV_DIR="$HOME/autoenv"
TIMESTAMP=$(date +%Y%m%d_%H%M)
LOG_DIR=$HOME/auto_ci_daily_logs
FUEL_TMP=/tmp/fuel_tmp

# POD and SCENARIO details used during OPNFV deployment performed by daily job
NODE_NAME=${NODE_NAME:-"ericsson-virtual1"}
POD_LAB=$(echo $NODE_NAME | cut -d '-' -f1)
POD_NAME=$(echo $NODE_NAME | cut -d '-' -f2)
DEPLOY_SCENARIO=${DEPLOY_SCENARIO:-"os-nofeature-onap-ha"}

#
# functions
#
# execute pylint and yamllint to check code quality
function execute_auto_lint_check() {
    if ! ./check -b ; then
        EXIT=$EXIT_LINT_FAILED
    fi
}

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

# create log dir if needed
if [ ! -e $LOG_DIR ] ; then
    echo "Create AUTO LOG DIRECTORY"
    echo "========================="
    echo "mkdir $LOG_DIR"
    mkdir $LOG_DIR
fi

# execute job based on passed parameter
case $1 in
    "verify")
        echo "==============="
        echo "AUTO verify job"
        echo "==============="

        execute_auto_lint_check
        #execute_auto_doc_check

        # Everything went well, so report SUCCESS to Jenkins
        exit $EXIT
        ;;
    "merge")
        echo "=============="
        echo "AUTO merge job"
        echo "=============="

        execute_auto_lint_check
        #execute_auto_doc_check

        # propagate result to the Jenkins job
        exit $EXIT
        ;;
    "daily")
        echo "=============="
        echo "AUTO daily job"
        echo "=============="
        echo
        echo "POD details:"
        echo "  LAB:  $POD_LAB"
        echo "  NAME: $POD_NAME"
        echo

        # clone fuel and execute installation of ONAP scenario to install
        # ONAP on top of OPNFV deployment
        [ -e fuel ] && rm -rf fuel
        git clone https://gerrit.opnfv.org/gerrit/fuel
        cd fuel
        # temporary until patch will be merged
        git pull https://gerrit.opnfv.org/gerrit/fuel refs/changes/69/64369/51

        echo "Installation of OPNFV and ONAP"
        echo "=============================="
        sudo ci/deploy.sh -l $POD_LAB -p $POD_NAME -s $DEPLOY_SCENARIO \
            -S $FUEL_TMP | tee $LOG_DIR/deploy_${TIMESTAMP}.log

        # propagate result to the Jenkins job
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
