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

# This module: management of test definitions

# Functions and classes to manage and initialize test data relative to:
#   physical resources
#   cloud resources
#   VNFs
#   recipients (OS, cloud/VNF managers)
#   challenge definitions
#   optional metrics
#   test definitions
# Storage of definition data in binary files (pickle), and test data results in .CSV files


#docstring
"""This module contains functions and classes to manage OPNFV Auto Test Data for Use Case 2: Resilience Improvements Through ONAP.
Auto project: https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095
"""


######################################################################
# import statements
import pickle
import csv
import sys
from enum import Enum
from datetime import datetime, timedelta
import AutoResilGlobal
#import openstack

# Constants with definition file names
FILE_PHYSICAL_RESOURCES =       "ResourcesPhysical.bin"
FILE_CLOUD_RESOURCES =          "ResourcesCloud.bin"
FILE_VNFS_SERVICES =            "ResourcesVNFServices.bin"
FILE_RECIPIENTS =               "Recipients.bin"
FILE_TEST_CASES =               "TestCases.bin"
FILE_METRIC_DEFINITIONS =       "DefinitionsMetrics.bin"
FILE_CHALLENGE_DEFINITIONS =    "DefinitionsChallenges.bin"
FILE_TEST_DEFINITIONS =         "DefinitionsTests.bin"

# Other constants
INDENTATION_MULTIPLIER =        4


######################################################################

def read_list_bin(file_name):
    """Generic function to extract a list from a binary file."""
    try:
        extracted_list = []
        with open(file_name, "rb") as binary_file:
            extracted_list = pickle.load(binary_file)
        return extracted_list
    except FileNotFoundError:
        print("File not found: ",file_name)
    except Exception as e:
        print(type(e), e)
        sys.exit()


def write_list_bin(inserted_list, file_name):
    """Generic function to write a list to a binary file (replace content)."""
    try:
        with open(file_name, "wb") as binary_file:
            pickle.dump(inserted_list, binary_file)
    except Exception as e:
        print(type(e), e)
        sys.exit()


class AutoBaseObject:
    """Base class for Auto project, with common attributes (ID, name)."""
    def __init__ (self, param_ID, param_name):
        self.ID = param_ID
        self.name = param_name
    # for display
    def __repr__(self):
        return ("ID="+str(self.ID)+" name="+self.name)
    # for print
    def __str__(self):
        return ("ID="+str(self.ID)+" name="+self.name)


def index_already_there(index, given_list):
    """Generic function to check if an index already exists in a list of AutoBaseObject."""

    # check if ID already exists
    already_there = False
    if len(given_list)>0:
        for item in given_list:
            if isinstance(item, AutoBaseObject):
                if item.ID == index:
                    already_there = True
                    break
            else:
                print("Issue with list: item is not AutoBaseObject")
                print(" index=\n",index)
                sys.exit()
    return already_there


def get_indexed_item_from_list(index, given_list):
    """Generic function to get an indexed entry from a list of AutoBaseObject."""

    returned_item = None

    if len(given_list)>0:
        for item in given_list:
            if isinstance(item, AutoBaseObject):
                if item.ID == index:
                    returned_item = item
                    break
            else:
                print("Issue with list: item is not AutoBaseObject")
                print(" index=\n",index)
                sys.exit()
    return returned_item


def get_indexed_item_from_file(index, file_name):
    """Generic function to get an indexed entry from a list of AutoBaseObject stored in a binary file."""

    list_in_file = read_list_bin(file_name)
    return get_indexed_item_from_list(index, list_in_file)



######################################################################

class TestCase(AutoBaseObject):
    """Test Case class for Auto project."""
    def __init__ (self, test_case_ID, test_case_name,
                  test_case_JIRA_URL):

        # superclass constructor
        AutoBaseObject.__init__(self, test_case_ID, test_case_name)

        # specifics for this subclass

        # Auto JIRA link
        self.JIRA_URL = test_case_JIRA_URL

    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Test Case ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-JIRA URL:", self.JIRA_URL, sep='')


# no need for functions to remove data: ever-growing library, arbitrary ID
# initial version: should not even add data dynamically, in case object signature changes
# better stick to initialization functions only to fill data, unless 100% sure signature does not change
def add_test_case_to_file(test_case_ID, test_case_name, test_case_JIRA_URL):
    """Function to add persistent data about test cases (in binary file)."""

    test_cases = read_list_bin(FILE_TEST_CASES)

    if index_already_there(test_case_ID, test_cases):
        print("Test Case ID=",test_case_ID," is already defined and can't be added")
    else:
        test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))
        write_list_bin(test_cases, FILE_TEST_CASES)

    return test_cases



def init_test_cases():
    """Function to initialize test case data."""
    test_cases = []

    # add info to list in memory, one by one, following signature values
    test_case_ID = 1
    test_case_name = "auto-resiliency-pif-001"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-9"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 2
    test_case_name = "auto-resiliency-pif-002"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-10"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 3
    test_case_name = "auto-resiliency-pif-003"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-11"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 4
    test_case_name = "auto-resiliency-pif-004"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-12"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 5
    test_case_name = "auto-resiliency-vif-001"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-13"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 6
    test_case_name = "auto-resiliency-vif-002"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-14"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 7
    test_case_name = "auto-resiliency-vif-003"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-15"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 8
    test_case_name = "auto-resiliency-sec-001"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-16"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 9
    test_case_name = "auto-resiliency-sec-002"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-17"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    test_case_ID = 10
    test_case_name = "auto-resiliency-sec-003"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-18"
    test_cases.append(TestCase(test_case_ID, test_case_name, test_case_JIRA_URL))

    # write list to binary file
    write_list_bin(test_cases, FILE_TEST_CASES)

    return test_cases


######################################################################

class TestDefinition(AutoBaseObject):
    """Test Definition class for Auto project."""
    def __init__ (self, test_def_ID, test_def_name,
                  test_def_challengeDefID,
                  test_def_testCaseID,
                  test_def_VNFIDs,
                  test_def_associatedMetricsIDs,
                  test_def_recipientIDs,
                  test_def_testCLICommandSent,
                  test_def_testAPICommandSent,
                  test_def_codeID):

        # superclass constructor
        AutoBaseObject.__init__(self, test_def_ID, test_def_name)

        # specifics for this subclass

        # associated Challenge Definition (ID)
        self.challenge_def_ID = test_def_challengeDefID
        # associated Test Case (ID)
        self.test_case_ID = test_def_testCaseID
        # associated VNFs (list of IDs)
        self.VNF_ID_list = test_def_VNFIDs
        # associated Metrics (list of IDs)
        self.associated_metrics_ID_list = test_def_associatedMetricsIDs
        # associated Recipients (list of IDs)
        self.recipient_ID_list = test_def_recipientIDs
        # associated test CLI commands to Recipients (list of strings)
        self.test_CLI_command_sent_list = test_def_testCLICommandSent
        # associated test API commands to Recipients (list of data objects)
        self.test_API_command_sent_list = test_def_testAPICommandSent

        # constant for total number of test codes (one of them is used per TestDefinition instance); would be 1 per test case
        self.TOTAL_NUMBER_OF_TEST_CODES = 10
        # chosen test code ID (the ID is an index in a list of method names) for this instance; convention: [1;N]; in list, index is [0;N-1]
        # a test code could use for instance Python clients (for OpenStack, Kubernetes, etc.), or HTTP APIs, or some of the CLI/API commands
        try:
            if 1 <= test_def_codeID <= self.TOTAL_NUMBER_OF_TEST_CODES:
                self.test_code_ID = test_def_codeID
            else:
                print("TestDefinition constructor: incorrect test_def_codeID=",test_def_codeID)
                sys.exit()  # stop entire program, because code ID MUST be correct
        except Exception as e:
            print(type(e), e)
            sys.exit()  # stop entire program, because code ID MUST be correct

        self.test_code_list = []  # list of method names; leave as per-object method (i.e. not as class methods or as static methods)
        # add one by one, for easier later additions of new methods
        self.test_code_list.append(self.test_code001)
        self.test_code_list.append(self.test_code002)
        self.test_code_list.append(self.test_code003)
        self.test_code_list.append(self.test_code004)
        self.test_code_list.append(self.test_code005)
        self.test_code_list.append(self.test_code006)
        self.test_code_list.append(self.test_code007)
        self.test_code_list.append(self.test_code008)
        self.test_code_list.append(self.test_code009)
        self.test_code_list.append(self.test_code010)


    def run_test_code(self):
        """Run currently selected test code. Common code runs here, specific code is invoked through test_code_list and test_code_ID."""
        try:
            # here, trigger start code from challenge def (to simulate VM failure), manage Recovery time measurement,
            # specific monitoring of VNF, trigger stop code from challenge def

            time1 = datetime.now()  # get time as soon as execution starts

            # create challenge execution instance
            chall_exec_ID = 1  # ideally, would be incremented, but need to maintain a number of challenge executions somewhere. or could be random.
            chall_exec_name = 'challenge execution'  # challenge def ID is already passed
            chall_exec_challDefID = self.challenge_def_ID
            chall_exec = ChallengeExecution(chall_exec_ID, chall_exec_name, chall_exec_challDefID)
            chall_exec.log.append_to_list('challenge execution created')

            # create test execution instance
            test_exec_ID = 1  # ideally, would be incremented, but need to maintain a number of text executions somewhere. or could be random.
            test_exec_name = 'test execution'  # test def ID is already passed
            test_exec_testDefID = self.ID
            test_exec_userID = ''  # or get user name from getpass module: import getpass and test_exec_userID = getpass.getuser()
            test_exec = TestExecution(test_exec_ID, test_exec_name, test_exec_testDefID, chall_exec_ID, test_exec_userID)
            test_exec.log.append_to_list('test execution created')

            # get time1 before anything else, so the setup time is counted
            test_exec.start_time = time1

            # get challenge definition instance, and start challenge
            challenge_def = get_indexed_item_from_list(self.challenge_def_ID, AutoResilGlobal.challenge_definition_list)
            challenge_def.run_start_challenge_code()

            # memorize challenge start time
            chall_exec.start_time = datetime.now()
            test_exec.challenge_start_time = chall_exec.start_time

            # call specific test definition code, via table of functions; this code should monitor a VNF and return when restoration is observed
            test_code_index = self.test_code_ID - 1  # lists are indexed from 0 to N-1
            self.test_code_list[test_code_index]()   # invoke corresponding method, via index; could check for return code

            # memorize restoration detection time and compute recovery time
            test_exec.restoration_detection_time = datetime.now()
            recovery_time_metric_def = get_indexed_item_from_file(1,FILE_METRIC_DEFINITIONS)  # get Recovery Time metric definition: ID=1
            test_exec.recovery_time = recovery_time_metric_def.compute(test_exec.challenge_start_time, test_exec.restoration_detection_time)

            # stop challenge
            challenge_def.run_stop_challenge_code()

            # memorize challenge stop time
            chall_exec.stop_time = datetime.now()
            chall_exec.log.append_to_list('challenge execution finished')

            # write results to CSV files, memorize test finish time
            chall_exec.write_to_csv()
            test_exec.finish_time = datetime.now()
            test_exec.log.append_to_list('test execution finished')
            test_exec.write_to_csv()


        except Exception as e:
            print(type(e), e)
            sys.exit()


    # library of test codes, probably 1 per test case, so test_case_ID would be the same as test_code_ID
    def test_code001(self):
        """Test case code number 001."""
        print("This is test_code001 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code002(self):
        """Test case code number 002."""
        print("This is test_code002 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code003(self):
        """Test case code number 003."""
        print("This is test_code003 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code004(self):
        """Test case code number 004."""
        print("This is test_code004 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code005(self):
        """Test case code number 005."""
        print("This is test_code005 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

        # specific VNF recovery monitoring, specific metrics if any
        # interact with ONAP, periodic query about VNF status; may also check VM or container status directly with VIM
        # return when VNF is recovered
        # may provision for failure to recover (max time to wait; return code: recovery OK boolean)

    def test_code006(self):
        """Test case code number 006."""
        print("This is test_code006 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code007(self):
        """Test case code number 007."""
        print("This is test_code007 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code008(self):
        """Test case code number 008."""
        print("This is test_code008 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code009(self):
        """Test case code number 009."""
        print("This is test_code009 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')

    def test_code010(self):
        """Test case code number 010."""
        print("This is test_code010 from TestDefinition #", self.ID, ", test case #", self.test_case_ID, sep='')


    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "\nTest Definition ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-associated test case ID:", self.test_case_ID, sep='')
        test_case = get_indexed_item_from_list(self.test_case_ID, AutoResilGlobal.test_case_list)
        if test_case != None:
            test_case.printout_all(indent_level+1)

        print(indent, "|-test code ID:", self.test_code_ID, sep='')

        print(indent, "|-associated challenge def ID:", self.challenge_def_ID, sep='')
        challenge_def = get_indexed_item_from_list(self.challenge_def_ID, AutoResilGlobal.challenge_definition_list)
        if challenge_def != None:
            challenge_def.printout_all(indent_level+1)

        if self.VNF_ID_list != None:
            if len(self.VNF_ID_list) >0:
                print(indent, "|-associated VNFs:", sep='')
                for VNF_ID in self.VNF_ID_list:
                    VNF_item = get_indexed_item_from_list(VNF_ID, AutoResilGlobal.VNF_Service_list)
                    if VNF_item != None:
                        VNF_item.printout_all(indent_level+1)

        if self.associated_metrics_ID_list != None:
            if len(self.associated_metrics_ID_list) >0:
                print(indent, "|-associated metrics:", sep='')
                for Metric_ID in self.associated_metrics_ID_list:
                    Metric_item = get_indexed_item_from_list(Metric_ID, AutoResilGlobal.metric_definition_list)
                    if Metric_item != None:
                        Metric_item.printout_all(indent_level+1)

        if self.recipient_ID_list != None:
            if len(self.recipient_ID_list) >0:
                print(indent, "|-associated recipients:", sep='')
                for recipient_ID in self.recipient_ID_list:
                    recipient_item = get_indexed_item_from_list(recipient_ID, AutoResilGlobal.recipient_list)
                    if recipient_item != None:
                        recipient_item.printout_all(indent_level+1)

        if self.test_CLI_command_sent_list != None:
            if len(self.test_CLI_command_sent_list) >0:
                print(indent, "|-associated CLI commands:", sep='')
                for CLI_command in self.test_CLI_command_sent_list:
                    print(" "*INDENTATION_MULTIPLIER, "|- ", CLI_command, sep='')

        # TODO: self.test_API_command_sent_list (depends how API commands are stored: likely a list of strings)



def init_test_definitions():
    """Function to initialize test definition data."""
    test_definitions = []

    # add info to list in memory, one by one, following signature values
    test_def_ID = 5
    test_def_name = "VM failure impact on virtual firewall (vFW VNF)"
    test_def_challengeDefID = 5
    test_def_testCaseID = 5
    test_def_VNFIDs = [1]
    test_def_associatedMetricsIDs = [2]
    test_def_recipientIDs = [2]
    test_def_testCLICommandSent = ["pwd","kubectl describe pods --include-uninitialized=false"]
    test_def_testAPICommandSent = ["data1","data2"]
    test_def_testCodeID = 5
    test_definitions.append(TestDefinition(test_def_ID, test_def_name,
                                           test_def_challengeDefID,
                                           test_def_testCaseID,
                                           test_def_VNFIDs,
                                           test_def_associatedMetricsIDs,
                                           test_def_recipientIDs,
                                           test_def_testCLICommandSent,
                                           test_def_testAPICommandSent,
                                           test_def_testCodeID))

    # write list to binary file
    write_list_bin(test_definitions, FILE_TEST_DEFINITIONS)

    return test_definitions


######################################################################

class ChallengeType(Enum):
    # physical server-level failures 1XX
    COMPUTE_HOST_FAILURE = 100
    DISK_FAILURE = 101
    LINK_FAILURE = 102
    NIC_FAILURE = 103

    # cloud-level failures 2XX
    CLOUD_COMPUTE_FAILURE = 200
    SDN_C_FAILURE = 201
    OVS_BRIDGE_FAILURE = 202
    CLOUD_STORAGE_FAILURE = 203
    CLOUD_NETWORK_FAILURE = 204

    # security stresses 3XX
    HOST_TAMPERING = 300
    HOST_INTRUSION = 301
    NETWORK_INTRUSION = 302


class ChallengeDefinition(AutoBaseObject):
    """Challenge Definition class for Auto project."""
    def __init__ (self, chall_def_ID, chall_def_name,
                  chall_def_challengeType,
                  chall_def_recipientID,
                  chall_def_impactedCloudResourcesInfo,
                  chall_def_impactedCloudResourceIDs,
                  chall_def_impactedPhysResourcesInfo,
                  chall_def_impactedPhysResourceIDs,
                  chall_def_startChallengeCLICommandSent,
                  chall_def_stopChallengeCLICommandSent,
                  chall_def_startChallengeAPICommandSent,
                  chall_def_stopChallengeAPICommandSent,
                  chall_def_codeID):

        # superclass constructor
        AutoBaseObject.__init__(self, chall_def_ID, chall_def_name)

        # specifics for this subclass

        # info about challenge type, categorization
        self.challenge_type = chall_def_challengeType
        # recipient instance, to start/stop the challenge
        self.recipient_ID = chall_def_recipientID

        # free-form info about cloud virtual impacted resource(s)
        self.impacted_cloud_resources_info = chall_def_impactedCloudResourcesInfo
        # impacted resources (list of IDs, usually only 1)
        self.impacted_cloud_resource_ID_list = chall_def_impactedCloudResourceIDs

        # free-form info about physical impacted resource(s)
        self.impacted_phys_resources_info = chall_def_impactedPhysResourcesInfo
        # impacted resources (list of IDs, usually only 1)
        self.impacted_phys_resource_ID_list = chall_def_impactedPhysResourceIDs

        # if CLI; can include hard-coded references to resources
        self.start_challenge_CLI_command_sent = chall_def_startChallengeCLICommandSent
        # if CLI; to restore to normal
        self.stop_challenge_CLI_command_sent = chall_def_stopChallengeCLICommandSent
        # if API; can include hard-coded references to resources
        self.start_challenge_API_command_sent = chall_def_startChallengeAPICommandSent
        # if API; to restore to normal
        self.stop_challenge_API_command_sent = chall_def_stopChallengeAPICommandSent

        # constant for total number of challenge codes (one of them is used per ChallengeDefinition instance);
        # may be 1 per test case, maybe not (common challenges, could be re-used across test definitions and test cases)
        # start and stop challenges are strictly linked: exactly 1 Stop challenge for each Start challenge, so same ID for Start and for Stop
        self.TOTAL_NUMBER_OF_CHALLENGE_CODES = 10

        # chosen start/stop challenge code ID (the ID is an index in a list of method names) for this instance;
        # convention: [1;N]; in list, index is [0;N-1]
        # a challenge code could use for instance Python clients (for OpenStack, Kubernetes, etc.), or HTTP APIs, or some of the CLI/API commands
        try:
            if 1 <= chall_def_codeID <= self.TOTAL_NUMBER_OF_CHALLENGE_CODES:
                self.challenge_code_ID = chall_def_codeID
            else:
                print("ChallengeDefinition constructor: incorrect chall_def_codeID=",chall_def_codeID)
                sys.exit()  # stop entire program, because code ID MUST be correct
        except Exception as e:
            print(type(e), e)
            sys.exit()  # stop entire program, because code ID MUST be correct

        # list of method names; leave as per-object method (i.e. not as class methods or as static methods)
        self.start_challenge_code_list = []
        self.stop_challenge_code_list = []
        # add one by one, for easier later additions of new methods; MUST be same index for Start and for Stop
        self.start_challenge_code_list.append(self.start_challenge_code001)
        self.stop_challenge_code_list.append(self.stop_challenge_code001)
        self.start_challenge_code_list.append(self.start_challenge_code002)
        self.stop_challenge_code_list.append(self.stop_challenge_code002)
        self.start_challenge_code_list.append(self.start_challenge_code003)
        self.stop_challenge_code_list.append(self.stop_challenge_code003)
        self.start_challenge_code_list.append(self.start_challenge_code004)
        self.stop_challenge_code_list.append(self.stop_challenge_code004)
        self.start_challenge_code_list.append(self.start_challenge_code005)
        self.stop_challenge_code_list.append(self.stop_challenge_code005)
        self.start_challenge_code_list.append(self.start_challenge_code006)
        self.stop_challenge_code_list.append(self.stop_challenge_code006)
        self.start_challenge_code_list.append(self.start_challenge_code007)
        self.stop_challenge_code_list.append(self.stop_challenge_code007)
        self.start_challenge_code_list.append(self.start_challenge_code008)
        self.stop_challenge_code_list.append(self.stop_challenge_code008)
        self.start_challenge_code_list.append(self.start_challenge_code009)
        self.stop_challenge_code_list.append(self.stop_challenge_code009)
        self.start_challenge_code_list.append(self.start_challenge_code010)
        self.stop_challenge_code_list.append(self.stop_challenge_code010)


    def run_start_challenge_code(self):
        """Run currently selected challenge code, start portion."""
        try:
            code_index = self.challenge_code_ID - 1  # lists are indexed from 0 to N-1
            self.start_challenge_code_list[code_index]()   # invoke corresponding start method, via index
        except Exception as e:
            print(type(e), e)
            sys.exit()

    def run_stop_challenge_code(self):
        """Run currently selected challenge code, stop portion."""
        try:
            code_index = self.challenge_code_ID - 1  # lists are indexed from 0 to N-1
            self.stop_challenge_code_list[code_index]()   # invoke corresponding stop method, via index
        except Exception as e:
            print(type(e), e)
            sys.exit()



    # library of challenge codes
    def start_challenge_code001(self):
        """Start Challenge code number 001."""
        print("This is start_challenge_code001 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code001(self):
        """Stop Challenge code number 001."""
        print("This is stop_challenge_code001 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code002(self):
        """Start Challenge code number 002."""
        print("This is start_challenge_code002 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code002(self):
        """Stop Challenge code number 002."""
        print("This is stop_challenge_code002 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code003(self):
        """Start Challenge code number 003."""
        print("This is start_challenge_code003 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code003(self):
        """Stop Challenge code number 003."""
        print("This is stop_challenge_code003 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code004(self):
        """Start Challenge code number 004."""
        print("This is start_challenge_code004 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code004(self):
        """Stop Challenge code number 004."""
        print("This is stop_challenge_code004 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code005(self):
        """Start Challenge code number 005."""
        print("This is start_challenge_code005 from ChallengeDefinition #",self.ID, sep='')
        # challenge #5, related to test case #5, i.e. test def #5
        # cloud reference (name and region) should be in clouds.yaml file
        # conn = openstack.connect(cloud='cloudNameForChallenge005', region_name='regionNameForChallenge005')
        # TestDef knows VNF, gets VNF->VM mapping from ONAP, passes VM ref to ChallengeDef
        # ChallengeDef suspends/resumes VM
        # conn.compute.servers() to get list of servers, using VM ID, check server.id and/or server.name
        # conn.compute.suspend_server(this server id)


    def stop_challenge_code005(self):
        """Stop Challenge code number 005."""
        print("This is stop_challenge_code005 from ChallengeDefinition #",self.ID, sep='')
        # challenge #5, related to test case #5, i.e. test def #5
        # cloud reference (name and region) should be in clouds.yaml file
        # conn = openstack.connect(cloud='cloudNameForChallenge005', region_name='regionNameForChallenge005')
        # TestDef knows VNF, gets VNF->VM mapping from ONAP, passes VM ref to ChallengeDef
        # ChallengeDef suspends/resumes VM
        # conn.compute.servers() to get list of servers, using VM ID, check server.id and/or server.name
        # conn.compute.conn.compute.resume_server(this server id)


    def start_challenge_code006(self):
        """Start Challenge code number 006."""
        print("This is start_challenge_code006 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code006(self):
        """Stop Challenge code number 006."""
        print("This is stop_challenge_code006 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code007(self):
        """Start Challenge code number 007."""
        print("This is start_challenge_code007 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code007(self):
        """Stop Challenge code number 007."""
        print("This is stop_challenge_code007 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code008(self):
        """Start Challenge code number 008."""
        print("This is start_challenge_code008 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code008(self):
        """Stop Challenge code number 008."""
        print("This is stop_challenge_code008 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code009(self):
        """Start Challenge code number 009."""
        print("This is start_challenge_code009 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code009(self):
        """Stop Challenge code number 009."""
        print("This is stop_challenge_code009 from ChallengeDefinition #",self.ID, sep='')

    def start_challenge_code010(self):
        """Start Challenge code number 010."""
        print("This is start_challenge_code010 from ChallengeDefinition #",self.ID, sep='')
    def stop_challenge_code010(self):
        """Stop Challenge code number 010."""
        print("This is stop_challenge_code010 from ChallengeDefinition #",self.ID, sep='')



    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Challenge Definition ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-challenge type:", self.challenge_type, sep='')

        print(indent, "|-challenge code ID:", self.challenge_code_ID, sep='')

        print(indent, "|-associated recipient ID:", self.recipient_ID, sep='')
        recipient = get_indexed_item_from_list(self.recipient_ID, AutoResilGlobal.recipient_list)
        if recipient != None:
            recipient.printout_all(indent_level+1)

        print(indent, "|-info about cloud virtual impacted resource(s):", self.impacted_cloud_resources_info, sep='')

        if self.impacted_cloud_resource_ID_list != None:
            if len(self.impacted_cloud_resource_ID_list) >0:
                print(indent, "|-associated cloud virtual impacted resource(s):", sep='')
                for cloud_resource_ID in self.impacted_cloud_resource_ID_list:
                    cloud_resource_item = get_indexed_item_from_list(cloud_resource_ID, AutoResilGlobal.cloud_virtual_resource_list)
                    if cloud_resource_item != None:
                        cloud_resource_item.printout_all(indent_level+1)

        print(indent, "|-info about physical virtual impacted resource(s):", self.impacted_phys_resources_info, sep='')

        if self.impacted_phys_resource_ID_list != None:
            if len(self.impacted_phys_resource_ID_list) >0:
                print(indent, "|-associated physical impacted resource(s):", sep='')
                for phys_resource_ID in self.impacted_phys_resource_ID_list:
                    phys_resource_item = get_indexed_item_from_list(phys_resource_ID, AutoResilGlobal.physical_resource_list)
                    if phys_resource_item != None:
                        phys_resource_item.printout_all(indent_level+1)

        print(indent, "|-CLI command to start challenge:", self.start_challenge_CLI_command_sent, sep='')

        print(indent, "|-CLI command to stop challenge:", self.stop_challenge_CLI_command_sent, sep='')

        # TODO: self.start_challenge_API_command_sent (depends how API commands are stored: likely a list of strings)
        # TODO: self.stop_challenge_API_command_sent (depends how API commands are stored: likely a list of strings)




def init_challenge_definitions():
    """Function to initialize challenge definition data."""
    challenge_defs = []

    # add info to list in memory, one by one, following signature values
    chall_def_ID = 5
    chall_def_name = "VM failure"
    chall_def_challengeType = ChallengeType.CLOUD_COMPUTE_FAILURE
    chall_def_recipientID = 1
    chall_def_impactedCloudResourcesInfo = "OpenStack VM on ctl02 in Arm pod"
    chall_def_impactedCloudResourceIDs = [2]
    chall_def_impactedPhysResourcesInfo = "physical server XYZ"
    chall_def_impactedPhysResourceIDs = [1]
    chall_def_startChallengeCLICommandSent = "service nova-compute stop"
    chall_def_stopChallengeCLICommandSent = "service nova-compute restart"
	# OpenStack VM Suspend vs. Pause: suspend stores the state of VM on disk while pause stores it in memory (RAM)
    # in CLI:
	# $ nova suspend NAME
	# $ nova resume NAME
    # but better use openstack SDK

    chall_def_startChallengeAPICommandSent = []
    chall_def_stopChallengeAPICommandSent = []

    chall_def_codeID = 5

    challenge_defs.append(ChallengeDefinition(chall_def_ID, chall_def_name,
                                              chall_def_challengeType,
                                              chall_def_recipientID,
                                              chall_def_impactedCloudResourcesInfo,
                                              chall_def_impactedCloudResourceIDs,
                                              chall_def_impactedPhysResourcesInfo,
                                              chall_def_impactedPhysResourceIDs,
                                              chall_def_startChallengeCLICommandSent,
                                              chall_def_stopChallengeCLICommandSent,
                                              chall_def_startChallengeAPICommandSent,
                                              chall_def_stopChallengeAPICommandSent,
                                              chall_def_codeID))

    # write list to binary file
    write_list_bin(challenge_defs, FILE_CHALLENGE_DEFINITIONS)

    return challenge_defs


######################################################################

class Recipient(AutoBaseObject):
    """Recipient class for Auto project."""
    def __init__ (self, recipient_ID, recipient_name,
                  recipient_info,
                  recipient_versionInfo,
                  recipient_accessIPAddress,
                  recipient_accessURL,
                  recipient_userNameCreds,
                  recipient_passwordCreds,
                  recipient_keyCreds,
                  recipient_networkInfo):

        # superclass constructor
        AutoBaseObject.__init__(self, recipient_ID, recipient_name)

        # specifics for this subclass

        # optional: free-form text info about recipient
        self.info = recipient_info
        # optional: version info
        self.version_info = recipient_versionInfo
        # optional: IP address of recipient
        self.access_IP_address = recipient_accessIPAddress
        # optional: URL of recipient
        self.access_URL = recipient_accessURL
        # optional: username for user/pwd credentials
        self.username_creds = recipient_userNameCreds
        # optional: password for user/pwd credentials
        self.password_creds = recipient_passwordCreds
        # optional: key credentials
        self.key_creds = recipient_keyCreds
        # optional: info about recipient's network (VPN, VCN, VN, Neutron, ...)
        self.network_info = recipient_networkInfo


    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Recipient ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-version info:", self.version_info, sep='')
        print(indent, "|-IP address:", self.access_IP_address, sep='')
        print(indent, "|-URL:", self.access_URL, sep='')
        print(indent, "|-username for user/pwd credentials:", self.username_creds, sep='')
        print(indent, "|-password for user/pwd credentials:", self.password_creds, sep='')
        print(indent, "|-key credentials:", self.key_creds, sep='')
        print(indent, "|-info about network:", self.network_info, sep='')



def init_recipients():
    """Function to initialize recipient data."""
    test_recipients = []

    # add info to list in memory, one by one, following signature values
    recipient_ID = 1
    recipient_name = "OpenStack on Arm pod"
    recipient_info = "controller resolves to one of the CTL VMs"
    recipient_versionInfo = ""
    recipient_accessIPAddress = "172.16.10.10"
    recipient_accessURL = ""
    recipient_userNameCreds = "ali"
    recipient_passwordCreds = "baba"
    recipient_keyCreds = "ssh-rsa k7fjsnEFzESfg6phg"
    recipient_networkInfo = "UNH IOL 172.16.0.0/22"

    test_recipients.append(Recipient(recipient_ID, recipient_name,
                                     recipient_info,
                                     recipient_versionInfo,
                                     recipient_accessIPAddress,
                                     recipient_accessURL,
                                     recipient_userNameCreds,
                                     recipient_passwordCreds,
                                     recipient_keyCreds,
                                     recipient_networkInfo))

    recipient_ID = 2
    recipient_name = "Kubernetes on x86 pod"
    recipient_info = "bare metal"
    recipient_versionInfo = "v1.9"
    recipient_accessIPAddress = "8.9.7.6"
    recipient_accessURL = ""
    recipient_userNameCreds = "kuber"
    recipient_passwordCreds = "netes"
    recipient_keyCreds = "ssh-rsa 0fjs7hjghsa37fhfs"
    recipient_networkInfo = "UNH IOL 10.10.30.157/22"


    test_recipients.append(Recipient(recipient_ID, recipient_name,
                                     recipient_info,
                                     recipient_versionInfo,
                                     recipient_accessIPAddress,
                                     recipient_accessURL,
                                     recipient_userNameCreds,
                                     recipient_passwordCreds,
                                     recipient_keyCreds,
                                     recipient_networkInfo))

    # write list to binary file
    write_list_bin(test_recipients, FILE_RECIPIENTS)

    return test_recipients


######################################################################

class MetricDefinition(AutoBaseObject):
    """Metric Definition class for Auto project. Actual metrics are subclasses with specific calculation methods."""
    def __init__ (self, metric_def_ID, metric_def_name,
                  metric_def_info):

        # superclass constructor
        AutoBaseObject.__init__(self, metric_def_ID, metric_def_name)

        # specifics for this subclass

        # optional: free-form text info about metric: formula, etc.
        self.info = metric_def_info


    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Metric Definition ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-info:", self.info, sep='')


class MetricValue:
    """Object for storing a measurement of a Metric Definition for Auto project, with common attributes
    (value, timestamp, metric_def_ID).
    """
    def __init__ (self, param_value, param_timestamp, param_metric_def_ID):
        self.value = param_value
        self.timestamp = param_timestamp
        self.metric_def_ID = param_metric_def_ID
    # for display
    def __repr__(self):
        return ("metric_def_ID="+str(self.metric_def_ID)+
                " value="+str(self.value)+
                " timestamp="+self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    # for print
    def __str__(self):
        return ("metric_def_ID="+str(self.metric_def_ID)+
                " value="+str(self.value)+
                " timestamp="+self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))


class RecoveryTimeDef(MetricDefinition):
    """Recovery Time Metric Definition class for Auto project.
    Formula: recovery_time = time_restoration_detected - time_challenge_started
    (measured duration between start of challenge (failure, stress, ...) and detection of restoration).
    Enter values as datetime objects.
    """
    def compute (self,
                 time_challenge_started, time_restoration_detected):
        """time_challenge_started: datetime object, time at which challenge was started;
        time_restoration_detected: datetime object, time at which restoration was detected;
        returns a MetricValue containing a timedelta object as value.
        """

        # a few checks first
        if time_challenge_started > time_restoration_detected:
            print("time_challenge_started should be <= time_restoration_detected")
            print("time_challenge_started=",time_challenge_started," time_restoration_detected=",time_restoration_detected)
            sys.exit()  # stop entire program, because formulas MUST be correct

        measured_metric_value = time_restoration_detected - time_challenge_started #difference between 2 datetime is a timedelta
        timestamp = datetime.now()

        return MetricValue(measured_metric_value, timestamp, self.ID)


class UptimePercentageDef(MetricDefinition):
    """Uptime Percentage Metric Definition class for Auto project.
    Formula: uptime / (reference_time - planned_downtime))
    Enter values in same unit (e.g., all in seconds, or all in minutes, or all in hours, etc.).
    """
    def compute (self,
                 measured_uptime, reference_time, planned_downtime):
        """measured_uptime: amount of time the service/system/resource was up and running;
        reference_time: amount of time during which the measurement was made;
        planned_downtime: amount to time during reference_time, which was planned to be down;
        returns a MetricValue object, with a value between 0 and 100.
        """

        # a few checks first
        if measured_uptime < 0.0:
            print("measured_uptime should be >= 0.0")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct
        if reference_time <= 0.0:
            print("reference_time should be > 0.0")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct
        if planned_downtime < 0.0:
            print("planned_downtime should be >= 0.0")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct
        if reference_time < planned_downtime:
            print("reference_time should be >= planned_downtime")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct
        if measured_uptime > reference_time:
            print("measured_uptime should be <= reference_time")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct
        if measured_uptime > (reference_time - planned_downtime):
            print("measured_uptime should be <= (reference_time - planned_downtime)")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because formulas MUST be correct

        measured_metric_value = 100 * measured_uptime / (reference_time - planned_downtime)
        timestamp = datetime.now()

        return MetricValue(measured_metric_value, timestamp, self.ID)



def init_metric_definitions():
    """Function to initialize metric definition data."""
    metric_definitions = []

    # add info to list in memory, one by one, following signature values
    metric_def_ID = 1
    metric_def_name = "Recovery Time"
    metric_def_info = "Measures time taken by ONAP to restore a VNF"
    metric_definitions.append(RecoveryTimeDef(metric_def_ID, metric_def_name,
                                              metric_def_info))

    metric_def_ID = 2
    metric_def_name = "Uptime Percentage"
    metric_def_info = "Measures ratio of uptime to reference time, not counting planned downtime"
    metric_definitions.append(UptimePercentageDef(metric_def_ID, metric_def_name,
                                                  metric_def_info))


    # write list to binary file
    write_list_bin(metric_definitions, FILE_METRIC_DEFINITIONS)

    return metric_definitions



######################################################################

class PhysicalResource(AutoBaseObject):
    """Physical Resource class for Auto project."""
    def __init__ (self, phys_resrc_ID, phys_resrc_name,
                  phys_resrc_info,
                  phys_resrc_IPAddress,
                  phys_resrc_MACAddress):

        # superclass constructor
        AutoBaseObject.__init__(self, phys_resrc_ID, phys_resrc_name)

        # specifics for this subclass

        # optional: free-form text info about physical resource
        self.info = phys_resrc_info
        # optional: main IP address of physical resource (e.g. management interface for a server)
        self.IP_address = phys_resrc_IPAddress
        # optional: main MAC address of physical resource
        self.MAC_address = phys_resrc_MACAddress


    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Physical Resource ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-info:", self.info, sep='')
        print(indent, "|-IP address:", self.IP_address, sep='')
        print(indent, "|-MAC address:", self.MAC_address, sep='')



def init_physical_resources():
    """Function to initialize physical resource data."""
    test_physical_resources = []

    # add info to list in memory, one by one, following signature values
    phys_resrc_ID = 1
    phys_resrc_name = "small-cavium-1"
    phys_resrc_info = "Jump server in Arm pod, 48 cores, 64G RAM, 447G SSD, aarch64 Cavium ThunderX, Ubuntu OS"
    phys_resrc_IPAddress = "10.10.50.12"
    phys_resrc_MACAddress = "00-14-22-01-23-45"

    test_physical_resources.append(PhysicalResource(phys_resrc_ID, phys_resrc_name,
                                                    phys_resrc_info,
                                                    phys_resrc_IPAddress,
                                                    phys_resrc_MACAddress))

    phys_resrc_ID = 2
    phys_resrc_name = "medium-cavium-1"
    phys_resrc_info = "Jump server in New York pod, 96 cores, 64G RAM, 447G SSD, aarch64 Cavium ThunderX, Ubuntu OS"
    phys_resrc_IPAddress = "30.31.32.33"
    phys_resrc_MACAddress = "0xb3:22:05:c1:aa:82"

    test_physical_resources.append(PhysicalResource(phys_resrc_ID, phys_resrc_name,
                                                    phys_resrc_info,
                                                    phys_resrc_IPAddress,
                                                    phys_resrc_MACAddress))

    phys_resrc_ID = 3
    phys_resrc_name = "mega-cavium-666"
    phys_resrc_info = "Jump server in Las Vegas, 1024 cores, 1024G RAM, 6666G SSD, aarch64 Cavium ThunderX, Ubuntu OS"
    phys_resrc_IPAddress = "54.53.52.51"
    phys_resrc_MACAddress = "01-23-45-67-89-ab"

    test_physical_resources.append(PhysicalResource(phys_resrc_ID, phys_resrc_name,
                                                    phys_resrc_info,
                                                    phys_resrc_IPAddress,
                                                    phys_resrc_MACAddress))


    # write list to binary file
    write_list_bin(test_physical_resources, FILE_PHYSICAL_RESOURCES)

    return test_physical_resources


######################################################################

class CloudVirtualResource(AutoBaseObject):
    """Cloud Virtual Resource class for Auto project."""
    def __init__ (self, cldvirtres_ID, cldvirtres_name,
                  cldvirtres_info,
                  cldvirtres_IPAddress,
                  cldvirtres_URL,
                  cldvirtres_related_phys_rsrcIDs):

        # superclass constructor
        AutoBaseObject.__init__(self, cldvirtres_ID, cldvirtres_name)

        # specifics for this subclass

        # optional: free-form text info about cloud virtual resource
        self.info = cldvirtres_info
        # optional: main IP address of cloud virtual resource (e.g. management interface for a virtual router)
        self.IP_address = cldvirtres_IPAddress
        # optional: URL address of cloud virtual resource
        self.URL = cldvirtres_URL
        # optional: related/associated physical resources (if known and useful or interesting, list of integer IDs)
        self.related_phys_rsrc_ID_list = cldvirtres_related_phys_rsrcIDs

    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "Cloud Virtual Resource ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-info:", self.info, sep='')
        print(indent, "|-IP address:", self.IP_address, sep='')
        print(indent, "|-URL:", self.URL, sep='')

        if self.related_phys_rsrc_ID_list != None:
            if len(self.related_phys_rsrc_ID_list) >0:
                print(indent, "|-related/associated physical resource(s):", sep='')
                for phys_resource_ID in self.related_phys_rsrc_ID_list:
                    phys_resource_item = get_indexed_item_from_list(phys_resource_ID, AutoResilGlobal.physical_resource_list)
                    if phys_resource_item != None:
                        phys_resource_item.printout_all(indent_level+1)


def init_cloud_virtual_resources():
    """Function to initialize cloud virtual resource data."""
    test_cldvirt_resources = []

    # add info to list in memory, one by one, following signature values
    cldvirtres_ID = 1
    cldvirtres_name = "nova-compute-1"
    cldvirtres_info = "nova VM in Arm pod"
    cldvirtres_IPAddress = "50.60.70.80"
    cldvirtres_URL = "http://50.60.70.80:8080"
    cldvirtres_related_phys_rsrcIDs = [1,3]

    test_cldvirt_resources.append(CloudVirtualResource(cldvirtres_ID, cldvirtres_name,
                                                       cldvirtres_info,
                                                       cldvirtres_IPAddress,
                                                       cldvirtres_URL,
                                                       cldvirtres_related_phys_rsrcIDs))

    cldvirtres_ID = 2
    cldvirtres_name = "nova-compute-2"
    cldvirtres_info = "nova VM in LaaS"
    cldvirtres_IPAddress = "50.60.70.80"
    cldvirtres_URL = "http://50.60.70.80:8080"
    cldvirtres_related_phys_rsrcIDs = [2,3]

    test_cldvirt_resources.append(CloudVirtualResource(cldvirtres_ID, cldvirtres_name,
                                                       cldvirtres_info,
                                                       cldvirtres_IPAddress,
                                                       cldvirtres_URL,
                                                       cldvirtres_related_phys_rsrcIDs))

    cldvirtres_ID = 3
    cldvirtres_name = "nova-compute-3"
    cldvirtres_info = "nova VM in x86 pod"
    cldvirtres_IPAddress = "50.60.70.80"
    cldvirtres_URL = "http://50.60.70.80:8080"
    cldvirtres_related_phys_rsrcIDs = [1]

    test_cldvirt_resources.append(CloudVirtualResource(cldvirtres_ID, cldvirtres_name,
                                                       cldvirtres_info,
                                                       cldvirtres_IPAddress,
                                                       cldvirtres_URL,
                                                       cldvirtres_related_phys_rsrcIDs))


    # write list to binary file
    write_list_bin(test_cldvirt_resources, FILE_CLOUD_RESOURCES)

    return test_cldvirt_resources


######################################################################

class VNFService(AutoBaseObject):
    """VNF or e2e Service class for Auto project."""
    def __init__ (self, vnf_serv_ID, vnf_serv_name,
                  vnf_serv_info,
                  vnf_serv_IPAddress,
                  vnf_serv_URL,
                  vnf_serv_related_phys_rsrcIDs,
                  vnf_serv_related_cloudvirt_rsrcIDs):

        # superclass constructor
        AutoBaseObject.__init__(self, vnf_serv_ID, vnf_serv_name)

        # specifics for this subclass

        # optional: free-form text info about VNF / e2e Service
        self.info = vnf_serv_info
        # optional: main IP address of VNF / e2e Service (e.g. management interface for a vCPE)
        self.IP_address = vnf_serv_IPAddress
        # optional: URL address of VNF / e2e Service
        self.URL = vnf_serv_URL
        # optional: related/associated physical resources (if known and useful or interesting, list of integer IDs)
        self.related_phys_rsrc_ID_list = vnf_serv_related_phys_rsrcIDs
        # optional: related/associated cloud virtual resources (if known and useful or interesting, list of integer IDs)
        self.related_cloud_virt_rsrc_ID_list = vnf_serv_related_cloudvirt_rsrcIDs


    def printout_all(self, indent_level):
        """Print out all attributes, with an indentation level."""
        indent = " "*indent_level*INDENTATION_MULTIPLIER

        print(indent, "VNF or e2e Service ID:", self.ID, sep='')
        print(indent, "|-name:", self.name, sep='')

        print(indent, "|-info:", self.info, sep='')
        print(indent, "|-IP address:", self.IP_address, sep='')
        print(indent, "|-URL:", self.URL, sep='')

        if self.related_phys_rsrc_ID_list != None:
            if len(self.related_phys_rsrc_ID_list) >0:
                print(indent, "|-related/associated physical resource(s):", sep='')
                for phys_resource_ID in self.related_phys_rsrc_ID_list:
                    phys_resource_item = get_indexed_item_from_list(phys_resource_ID, AutoResilGlobal.physical_resource_list)
                    if phys_resource_item != None:
                        phys_resource_item.printout_all(indent_level+1)

        if self.related_cloud_virt_rsrc_ID_list != None:
            if len(self.related_cloud_virt_rsrc_ID_list) >0:
                print(indent, "|-related/associated cloud virtual resource(s):", sep='')
                for cloud_resource_ID in self.related_cloud_virt_rsrc_ID_list:
                    cloud_resource_item = get_indexed_item_from_list(cloud_resource_ID, AutoResilGlobal.cloud_virtual_resource_list)
                    if cloud_resource_item != None:
                        cloud_resource_item.printout_all(indent_level+1)



def init_VNFs_Services():
    """Function to initialize VNFs and e2e Services data."""
    test_VNFs_Services = []

    # add info to list in memory, one by one, following signature values
    vnf_serv_ID = 1
    vnf_serv_name = "vCPE-1"
    vnf_serv_info = "virtual CPE in Arm pod"
    vnf_serv_IPAddress = "5.4.3.2"
    vnf_serv_URL = "http://5.4.3.2:8080"
    vnf_serv_related_phys_rsrcIDs = [1,2]
    vnf_serv_related_cloudvirt_rsrcIDs = [1]

    test_VNFs_Services.append(VNFService(vnf_serv_ID, vnf_serv_name,
                                         vnf_serv_info,
                                         vnf_serv_IPAddress,
                                         vnf_serv_URL,
                                         vnf_serv_related_phys_rsrcIDs,
                                         vnf_serv_related_cloudvirt_rsrcIDs))


    vnf_serv_ID = 2
    vnf_serv_name = "vFW-1"
    vnf_serv_info = "virtual Firewall in x86 pod"
    vnf_serv_IPAddress = "6.7.8.9"
    vnf_serv_URL = "http://6.7.8.9:8080"
    vnf_serv_related_phys_rsrcIDs = [3]
    vnf_serv_related_cloudvirt_rsrcIDs = [2,3]

    test_VNFs_Services.append(VNFService(vnf_serv_ID, vnf_serv_name,
                                         vnf_serv_info,
                                         vnf_serv_IPAddress,
                                         vnf_serv_URL,
                                         vnf_serv_related_phys_rsrcIDs,
                                         vnf_serv_related_cloudvirt_rsrcIDs))

    # write list to binary file
    write_list_bin(test_VNFs_Services, FILE_VNFS_SERVICES)

    return test_VNFs_Services



######################################################################

class TimeStampedStringList:
    """This is a utility class for Auto project, for execution classes (ChallengeExecution and TestExecution).
    It stores a list of timestrings and timestamps them.
    """
    def __init__ (self):
        self.__string_list = []
        self.__timestamp_list = []

    def append_to_list(self, string_to_append):
        """Append an object to a list of strings and adds a timestamp."""
        if type(string_to_append)==str:
            current_time = datetime.now()
            self.__string_list.append(string_to_append)
            self.__timestamp_list.append(current_time)  # timestamp will have the same index as string
        else:
            print("appended object must be a string, string_to_append=",string_to_append)
            sys.exit()  # stop entire program, because string MUST be correct

    def get_raw_list(self):
        return self.__string_list

    def get_raw_list_timestamps(self):
        return self.__timestamp_list

    def get_timestamped_strings(self):
        """return a list of strings with timestamps as prefixes (not showing microseconds)."""
        ret_list = []
        i = 0
        while i < len(self.__string_list):
            ret_list.append(self.__timestamp_list[i].strftime("%Y-%m-%d %H:%M:%S")+" "+self.__string_list[i])
            i += 1
        return ret_list

    def length(self):
        return len(self.__string_list)


######################################################################

class ChallengeExecution(AutoBaseObject):
    """Class for Auto project, tracking the execution details of a Challenge Definition,
    with a method to dump all results to a CSV file.
    """
    def __init__ (self, chall_exec_ID, chall_exec_name,
                  chall_exec_challDefID):

        # superclass constructor
        AutoBaseObject.__init__(self, chall_exec_ID, chall_exec_name)

        # specifics for this subclass

        # associated Challenge Definition (ID)
        self.challenge_def_ID = chall_exec_challDefID

        # attributes getting values during execution

        # associated Start and Stop times (when Challenge was started and stopped)
        self.start_time = None
        self.stop_time = None
        # log: list of strings, to capture any interesting or significant event
        self.log = TimeStampedStringList()
        # list of CLI responses
        self.CLI_responses = TimeStampedStringList()
        # list of API responses (convert to strings)
        self.API_responses = TimeStampedStringList()

    def write_to_csv(self):
        """Generic function to dump all Challenge Execution data in a CSV file."""

        dump_list = []

        # add rows one by one, each as a list, even if only 1 element

        dump_list.append(["challenge execution ID",self.ID])
        dump_list.append(["challenge execution name",self.name])

        dump_list.append(["challenge definition ID",self.challenge_def_ID])
        challenge_def_name = get_indexed_item_from_file(self.challenge_def_ID, FILE_CHALLENGE_DEFINITIONS)
        dump_list.append(["challenge definition name",challenge_def_name])

        if self.start_time != None:
            dump_list.append(["challenge start time",self.start_time.strftime("%Y-%m-%d %H:%M:%S")])
        if self.stop_time != None:
            dump_list.append(["challenge stop time",self.stop_time.strftime("%Y-%m-%d %H:%M:%S")])

        if self.log.length() > 0 :
            dump_list.append(["Log:"])
            for item in self.log.get_timestamped_strings():
                dump_list.append([item])

        if self.CLI_responses.length() > 0 :
            dump_list.append(["CLI responses:"])
            for item in self.CLI_responses.get_timestamped_strings():
                dump_list.append([item])

        if self.API_responses.length() > 0 :
            dump_list.append(["API responses:"])
            for item in self.API_responses.get_timestamped_strings():
                dump_list.append([item])

        try:
            # output CSV file name: challDefExec + ID + start time + .csv
            file_name = "challDefExec" + "{0:0=3d}".format(self.challenge_def_ID) + "-" + self.start_time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv"
            with open(file_name, "w", newline="") as file:
                csv_file_writer = csv.writer(file)
                csv_file_writer.writerows(dump_list)
        except Exception as e:
            print(type(e), e)
            sys.exit()



######################################################################

class TimeStampedMetricValueList:
    """This is a utility class for Auto project, for the test execution class (TestExecution).
    It stores a list of Metric Values (with their respective timestamps).
    """
    def __init__ (self):
        self.__metric_value_list = []

    def append_to_list(self, metric_value_to_append):
        """Append a metric value (MetricValue) to the list. MetricValue already has a timestamp attribute."""
        if type(metric_value_to_append)==MetricValue:
            self.__metric_value_list.append(metric_value_to_append)
        else:
            print("appended object must be a MetricValue, metric_value_to_append=",metric_value_to_append)
            sys.exit()  # stop entire program, because metric_value_to_append MUST be correct

    def get_raw_list(self):
        return self.__metric_value_list

    def get_timestamped_metric_values_as_strings(self):
        """Return a list of strings with metric values and timestamps as prefixes (not showing microseconds).
        Also show the metric def ID in parentheses.
        """
        ret_list = []
        i = 0
        while i < len(self.__metric_value_list):
            ret_list.append(self.__metric_value_list[i].timestamp.strftime("%Y-%m-%d %H:%M:%S") + " " +
                            str(self.__metric_value_list[i].value) +
                            "(" + str(self.__metric_value_list[i].metric_def_ID) + ")")
            i += 1
        return ret_list

    def length(self):
        return len(self.__metric_value_list)



######################################################################

class TestExecution(AutoBaseObject):
    """Class for Auto project, tracking the execution details of a Test Definition,
    with a method to dump all results to a CSV file.
    """
    def __init__ (self, test_exec_ID, test_exec_name,
                  test_exec_testDefID,
                  test_exec_challengeExecID,
                  test_exec_userID):

        # superclass constructor
        AutoBaseObject.__init__(self, test_exec_ID, test_exec_name)

        # specifics for this subclass

        # associated Test Definition (ID)
        self.test_def_ID = test_exec_testDefID
        # associated Challenge Execution (ID) (execution instance of a challenge definition); get challenge start time from it;
        self.challenge_exec_ID = test_exec_challengeExecID
        # associated User (ID)
        self.user_ID = test_exec_userID

        # attributes getting values during execution

        # associated Start and Finish times (when test was started and finished)
        self.start_time = None
        self.finish_time = None
        # time when the challenge was started [datetime]; same value as associated ChallengeExecution.start_time;
        # keep a copy here for print convenience;
        self.challenge_start_time = None
        # time when the VNF/service restoration (by ONAP) was detected by the test code [datetime]
        self.restoration_detection_time = None
        # key metric: recovery time, defined as time elapsed between start of challenge and restoration detection [timedelta]
        self.recovery_time = None
        # list of associated metric values
        self.associated_metric_values = TimeStampedMetricValueList()
        # log: list of strings, to capture any interesting or significant event
        self.log = TimeStampedStringList()
        # list of CLI responses
        self.CLI_responses = TimeStampedStringList()
        # list of API responses (convert to strings)
        self.API_responses = TimeStampedStringList()


    def write_to_csv(self):
        """Generic function to dump all Test Execution data in a CSV file."""

        dump_list = []

        # add rows one by one, each as a list, even if only 1 element

        dump_list.append(["test execution ID",self.ID])
        dump_list.append(["test execution name",self.name])

        dump_list.append(["test definition ID",self.test_def_ID])
        test_def_name = get_indexed_item_from_file(self.test_def_ID, FILE_TEST_DEFINITIONS)
        dump_list.append(["test definition name",test_def_name])

        dump_list.append(["associated challenge execution ID",self.challenge_exec_ID])
        dump_list.append(["user ID",self.user_ID])

        if self.start_time != None:
            dump_list.append(["test start time",self.start_time.strftime("%Y-%m-%d %H:%M:%S")])

        if self.finish_time != None:
            dump_list.append(["test finish time",self.finish_time.strftime("%Y-%m-%d %H:%M:%S")])

        if self.challenge_start_time != None:
            dump_list.append(["challenge stop time",self.challenge_start_time.strftime("%Y-%m-%d %H:%M:%S")])
        if self.restoration_detection_time != None:
            dump_list.append(["restoration detection time",self.restoration_detection_time.strftime("%Y-%m-%d %H:%M:%S")])
        if self.recovery_time != None:
            if self.recovery_time.value != None:
                if type(self.recovery_time.value)==timedelta:
                    # timedelta: days and seconds are attributes, total_seconds() is a method
                    dump_list.append(["MEASURED RECOVERY TIME (s)",self.recovery_time.value.total_seconds()])
                    rtday = self.recovery_time.value.days
                    rthrs = self.recovery_time.value.seconds // 3600
                    rtmin = (self.recovery_time.value.seconds % 3600) // 60
                    rtsec = self.recovery_time.value.seconds % 60
                    rtmil = self.recovery_time.value.microseconds
                    dump_list.append(["MEASURED RECOVERY TIME (days, hours, mins, seconds, microseconds)",
                                      rtday, rthrs, rtmin, rtsec, rtmil])

        if self.associated_metric_values.length() > 0 :
            dump_list.append(["Metric Values:"])
            for item in self.associated_metric_values.get_timestamped_metric_values_as_strings():
                dump_list.append([item])

        if self.log.length() > 0 :
            dump_list.append(["Log:"])
            for item in self.log.get_timestamped_strings():
                dump_list.append([item])

        if self.CLI_responses.length() > 0 :
            dump_list.append(["CLI responses:"])
            for item in self.CLI_responses.get_timestamped_strings():
                dump_list.append([item])

        if self.API_responses.length() > 0 :
            dump_list.append(["API responses:"])
            for item in self.API_responses.get_timestamped_strings():
                dump_list.append([item])

        try:
            # output CSV file name: testDefExec + ID + start time + .csv
            file_name = "testDefExec" + "{0:0=3d}".format(self.test_def_ID) + "-" + self.start_time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv"
            with open(file_name, "w", newline="") as file:
                csv_file_writer = csv.writer(file)
                csv_file_writer.writerows(dump_list)
        except Exception as e:
            print(type(e), e)
            sys.exit()


######################################################################
def dump_all_binaries_to_CSV():
    """Get all content from all Definition data binary files, and dump everything in a snapshot CSV file."""
    ## TODO
    timenow = datetime.now()


######################################################################
def main():


    # everything here is for unit-testing of this module; not part of actual code
    tcs = init_test_cases()
    print(tcs)

    test_case_ID = 33
    test_case_name = "auto-resiliency-xyz"
    test_case_JIRA_URL = "https://jira.opnfv.org/browse/AUTO-400"
    add_test_case_to_file(test_case_ID, test_case_name, test_case_JIRA_URL)
    print(read_list_bin(FILE_TEST_CASES))

    print(get_indexed_item_from_file(3,FILE_TEST_CASES))
    print(get_indexed_item_from_file(257,FILE_TEST_CASES))

    print("tcs[4]=",tcs[4])
    print(tcs[4].ID)
    print(tcs[4].name)
    print(tcs[4].JIRA_URL)

    print()

    challgs = init_challenge_definitions()
    print(challgs)
    chall = get_indexed_item_from_file(5,FILE_CHALLENGE_DEFINITIONS)
    print(chall)
    chall.run_start_challenge_code()
    chall.run_stop_challenge_code()

    print()

    tds = init_test_definitions()
    print(tds)
    td = get_indexed_item_from_file(5,FILE_TEST_DEFINITIONS)
    print(td)
    #td.printout_all(0)
    #td.run_test_code()

    print()

    rcps = init_recipients()
    print(rcps)
    rcp = get_indexed_item_from_file(1,FILE_RECIPIENTS)
    print(rcp)

    print()


    metricdefs = init_metric_definitions()
    print(metricdefs)

    metricdef = get_indexed_item_from_file(1,FILE_METRIC_DEFINITIONS)
    print(metricdef)
    t1 = datetime(2018,7,1,15,10,12,500000)
    t2 = datetime(2018,7,1,15,13,43,200000)
    r1 = metricdef.compute(t1,t2)
    print(r1)
    print()

    metricdef = get_indexed_item_from_file(2,FILE_METRIC_DEFINITIONS)
    print(metricdef)
    r1 = metricdef.compute(735, 1000, 20)
    r2 = metricdef.compute(980, 1000, 20)
    r3 = metricdef.compute(920.0, 1000.0, 0.0)
    r4 = metricdef.compute(920.0, 1500.0, 500.0)
    r5 = metricdef.compute(919.99999, 1000.0, 0.000001)
    print(r1)
    print(r2)
    print(r3)
    print(r4)
    print(r5)

    print()

    physRs = init_physical_resources()
    print(physRs)
    physR = get_indexed_item_from_file(1,FILE_PHYSICAL_RESOURCES)
    print(physR)

    print()

    cloudRs = init_cloud_virtual_resources()
    print(cloudRs)
    cloudR = get_indexed_item_from_file(1,FILE_CLOUD_RESOURCES)
    print(cloudR)

    print()

    VNFs = init_VNFs_Services()
    print(VNFs)
    VNF = get_indexed_item_from_file(1,FILE_VNFS_SERVICES)
    print(VNF)

    print()

    ce1 = ChallengeExecution(1,"essai challenge execution",5)
    ce1.start_time = datetime.now()
    ce1.log.append_to_list("challenge execution log event 1")
    ce1.log.append_to_list("challenge execution log event 2")
    ce1.CLI_responses.append_to_list("challenge execution CLI response 1")
    ce1.log.append_to_list("challenge execution log event 3")
    ce1.CLI_responses.append_to_list("challenge execution CLI response 2")
    ce1.log.append_to_list("challenge execution log event 4")
    ce1.log.append_to_list("challenge execution log event 5")
    ce1.API_responses.append_to_list("challenge execution API response 1")
    ce1.log.append_to_list("challenge execution log event 6")
    print("log length: ", ce1.log.length())
    print(ce1.log.get_timestamped_strings())
    print("CLI_responses length: ", ce1.CLI_responses.length())
    print(ce1.CLI_responses.get_timestamped_strings())
    print("API_responses length: ", ce1.API_responses.length())
    print(ce1.API_responses.get_timestamped_strings())
    ce1.stop_time = datetime.now()
    ce1.write_to_csv()

    print()

    te1 = TestExecution(1,"essai test execution",5,1,"Gerard")
    te1.start_time = datetime.now()
    te1.challenge_start_time = ce1.start_time  # illustrate how to set test execution challenge start time
    print("te1.challenge_start_time:",te1.challenge_start_time)

    te1.log.append_to_list("test execution log event 1")
    te1.log.append_to_list("test execution log event 2")
    te1.CLI_responses.append_to_list("test execution CLI response 1")
    te1.CLI_responses.append_to_list("test execution CLI response 2")

    metricdef = get_indexed_item_from_file(2,FILE_METRIC_DEFINITIONS)  # get a metric definition, some ID
    print(metricdef)
    r1 = metricdef.compute(735, 1000, 20)  # compute a metric value
    print(r1)
    te1.associated_metric_values.append_to_list(r1)  # append a measured metric value to test execution
    r1 = metricdef.compute(915, 1000, 20)  # compute a metric value
    print(r1)
    te1.associated_metric_values.append_to_list(r1)  # append a measured metric value to test execution

    te1.log.append_to_list("test execution log event 3")
    te1.API_responses.append_to_list("test execution API response 1")

    print("log length: ", te1.log.length())
    print(te1.log.get_timestamped_strings())
    print("CLI_responses length: ", te1.CLI_responses.length())
    print(te1.CLI_responses.get_timestamped_strings())
    print("API_responses length: ", te1.API_responses.length())
    print(te1.API_responses.get_timestamped_strings())
    print("associated_metric_values length: ", te1.associated_metric_values.length())
    print(te1.associated_metric_values.get_timestamped_metric_values_as_strings())

    te1.restoration_detection_time = datetime.now()
    print("te1.restoration_detection_time:",te1.restoration_detection_time)
    metricdef = get_indexed_item_from_file(1,FILE_METRIC_DEFINITIONS)  # get Recovery Time metric definition: ID=1
    print(metricdef)
    r1 = metricdef.compute(te1.challenge_start_time, te1.restoration_detection_time)  # compute a metric value, for Recovery time
    te1.recovery_time = r1  # assignment could be direct, i.e. te1.recovery_time = metricdef.compute(...)

    te1.finish_time = datetime.now()  # test execution is finished
    te1.write_to_csv()

    print()

    print("\nCiao")

if __name__ == "__main__":
    main()






