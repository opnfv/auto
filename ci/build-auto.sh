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
EXIT_FUEL_FAILED=10

#
# configuration
#
AUTOENV_DIR="$HOME/autoenv"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR=$HOME/auto_ci_daily_logs

# POD and SCENARIO details used during OPNFV deployment performed by daily job
NODE_NAME=${NODE_NAME:-"ericsson-virtual1"}
POD_LAB=$(echo $NODE_NAME | cut -d '-' -f1)
POD_NAME=$(echo $NODE_NAME | cut -d '-' -f2)
DEPLOY_SCENARIO=${DEPLOY_SCENARIO:-"os-nosdn-onap-ha"}

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
        echo "Deployment details:"
        echo "  LAB:      $POD_LAB"
        echo "  POD:      $POD_NAME"
        echo "  Scenario: $DEPLOY_SCENARIO"
        echo
        echo "Installation of OPNFV and ONAP"
        echo "=============================="
        # clone fuel and execute installation of ONAP scenario to install
        # ONAP on top of OPNFV deployment
        [ -e fuel ] && rm -rf fuel
        git clone https://gerrit.opnfv.org/gerrit/fuel
        cd fuel
        # Fuel master branch is currently broken; thus use stable/gambia
        # branch with recent master version of ONAP scenario
        git checkout stable/gambia
        git checkout origin/master mcp/config/states/onap \
            mcp/config/scenario/os-nosdn-onap-ha.yaml  \
            mcp/config/scenario/os-nosdn-onap-noha.yaml

        LOG_FILE="$LOG_DIR/deploy_${TIMESTAMP}.log"
        echo "ci/deploy.sh -l $POD_LAB -p $POD_NAME -s $DEPLOY_SCENARIO |&\
            tee $LOG_FILE"
        DEPLOY_START=$(date +%Y%m%d_%H%M%S)
        ci/deploy.sh -l $POD_LAB -p $POD_NAME -s $DEPLOY_SCENARIO |&\
            tee $LOG_FILE

        # report failure if fuel failed to install OPNFV or ONAP
        [ $? -ne 0 ] && exit $EXIT_FUEL_FAILED

        # process report
        DEPLOY_END=$(date +%Y%m%d_%H%M%S)
        REPORT_FILE="$LOG_DIR/deploy_report_${TIMESTAMP}.txt"
        CSV_SUMMARY="$LOG_DIR/deploy_summary_${TIMESTAMP}.csv"
        MARKER="ONAP INSTALLATION REPORT"
        sed -n "/^$MARKER/,/^END OF $MARKER/p;/^END OF $MARKER/q" \
            $LOG_FILE > $REPORT_FILE
        PODS_TOTAL=$(grep "PODs Total" $REPORT_FILE | sed -e 's/[^0-9]//g')
        PODS_FAILED=$(grep "PODs Failed" $REPORT_FILE | sed -e 's/[^0-9]//g')
        TC_SUM=$(grep "tests total" $REPORT_FILE | tail -n1 |\
            sed -e 's/[^0-9,]//g')

        echo "Start Time,End Time,Total PODs,Failed PODs,Total Tests,Passed"\
            "Tests,Failed Tests" >> $CSV_SUMMARY
        echo "$DEPLOY_START,$DEPLOY_END,$PODS_TOTAL,$PODS_FAILED,$TC_SUM"\
            >> $CSV_SUMMARY

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
