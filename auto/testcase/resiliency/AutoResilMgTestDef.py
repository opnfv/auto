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

# Constants with definition file names
FILE_PHYSICAL_RESOURCES =       "ResourcesPhysical.bin"
FILE_CLOUD_RESOURCES =          "ResourcesCloud.bin"
FILE_VNFS_SERVICES =            "ResourcesVNFServices.bin"
FILE_RECIPIENTS =               "Recipients.bin"
FILE_TEST_CASES =               "TestCases.bin"
FILE_METRIC_DEFINITIONS =       "DefinitionsMetrics.bin"
FILE_CHALLENGE_DEFINITIONS =    "DefinitionsChallenges.bin"
FILE_TEST_DEFINITIONS =         "DefinitionsTests.bin"


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
                  test_def_testAPICommandSent):

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


def init_test_definitions():
    """Function to initialize test definition data."""
    test_definitions = []

    # add info to list in memory, one by one, following signature values
    test_def_ID = 1
    test_def_name = "VM failure impact on virtual firewall (vFW VNF)"
    test_def_challengeDefID = 1
    test_def_testCaseID = 5
    test_def_VNFIDs = [1]
    test_def_associatedMetricsIDs = []
    test_def_recipientIDs = [2]
    test_def_testCLICommandSent = ["pwd"]
    test_def_testAPICommandSent = ["data1","data2"]
    test_definitions.append(TestDefinition(test_def_ID, test_def_name,
                                           test_def_challengeDefID,
                                           test_def_testCaseID,
                                           test_def_VNFIDs,
                                           test_def_associatedMetricsIDs,
                                           test_def_recipientIDs,
                                           test_def_testCLICommandSent,
                                           test_def_testAPICommandSent))

    # write list to binary file
    write_list_bin(test_definitions, FILE_TEST_DEFINITIONS)

    return test_definitions


######################################################################

class ChallengeType(Enum):
    # server-level failures
    COMPUTE_HOST_FAILURE = 100
    DISK_FAILURE = 101
    LINK_FAILURE = 102
    NIC_FAILURE = 103
    # network-level failures
    OVS_BRIDGE_FAILURE = 200
    # security stresses
    HOST_TAMPERING = 300
    HOST_INTRUSION = 301
    NETWORK_INTRUSION = 302


class ChallengeDefinition(AutoBaseObject):
    """Challenge Definition class for Auto project."""
    def __init__ (self, chall_def_ID, chall_def_name,
                  chall_def_challengeType,
                  chall_def_recipientID,
                  chall_def_impactedResourcesInfo,
                  chall_def_impactedResourceIDs,
                  chall_def_startChallengeCLICommandSent,
                  chall_def_stopChallengeCLICommandSent,
                  chall_def_startChallengeAPICommandSent,
                  chall_def_stopChallengeAPICommandSent):

        # superclass constructor
        AutoBaseObject.__init__(self, chall_def_ID, chall_def_name)

        # specifics for this subclass

        # info about challenge type, categorization
        self.challenge_type = chall_def_challengeType
        # recipient instance, to start/stop the challenge
        self.recipient_ID = chall_def_recipientID
        # free-form info about impacted resource(s)
        self.impacted_resources_info = chall_def_impactedResourcesInfo
        # impacted resources (list of IDs, usually only 1)
        self.impacted_resource_ID_list = chall_def_impactedResourceIDs
        # if CLI; can include hard-coded references to resources
        self.start_challenge_CLI_command_sent = chall_def_startChallengeCLICommandSent
        # if CLI; to restore to normal
        self.stop_challenge_CLI_command_sent = chall_def_stopChallengeCLICommandSent
        # if API; can include hard-coded references to resources
        self.start_challenge_API_command_sent = chall_def_startChallengeAPICommandSent
        # if API; to restore to normal
        self.stop_challenge_API_command_sent = chall_def_stopChallengeAPICommandSent


def init_challenge_definitions():
    """Function to initialize challenge definition data."""
    challenge_defs = []

    # add info to list in memory, one by one, following signature values
    chall_def_ID = 1
    chall_def_name = "VM failure"
    chall_def_challengeType = ChallengeType.COMPUTE_HOST_FAILURE
    chall_def_recipientID = 1
    chall_def_impactedResourcesInfo = "OpenStack VM on ctl02 in Arm pod"
    chall_def_impactedResourceIDs = [2]
    chall_def_startChallengeCLICommandSent = "service nova-compute stop"
    chall_def_stopChallengeCLICommandSent = "service nova-compute restart"
    chall_def_startChallengeAPICommandSent = []
    chall_def_stopChallengeAPICommandSent = []

    challenge_defs.append(ChallengeDefinition(chall_def_ID, chall_def_name,
                                              chall_def_challengeType,
                                              chall_def_recipientID,
                                              chall_def_impactedResourcesInfo,
                                              chall_def_impactedResourceIDs,
                                              chall_def_startChallengeCLICommandSent,
                                              chall_def_stopChallengeCLICommandSent,
                                              chall_def_startChallengeAPICommandSent,
                                              chall_def_stopChallengeAPICommandSent))

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
        # optional: password for user/pwd credentials
        self.key_creds = recipient_keyCreds
        # optional: info about recipient's network (VPN, VCN, VN, Neutron, ...)
        self.network_info = recipient_networkInfo


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
    recipient_networkInfo = "UNH IOL 172.16.0.0/16"

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
            sys.exit()  # stop entire program, because fomulas MUST be correct

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
            sys.exit()  # stop entire program, because fomulas MUST be correct
        if reference_time <= 0.0:
            print("reference_time should be > 0.0")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because fomulas MUST be correct
        if planned_downtime < 0.0:
            print("planned_downtime should be >= 0.0")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because fomulas MUST be correct
        if reference_time < planned_downtime:
            print("reference_time should be >= planned_downtime")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because fomulas MUST be correct
        if measured_uptime > reference_time:
            print("measured_uptime should be <= reference_time")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because fomulas MUST be correct
        if measured_uptime > (reference_time - planned_downtime):
            print("measured_uptime should be <= (reference_time - planned_downtime)")
            print("meas=",measured_uptime," ref=",reference_time," pla=",planned_downtime)
            sys.exit()  # stop entire program, because fomulas MUST be correct

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


def init_physical_resources():
    """Function to initialize physical resource data."""
    test_physical_resources = []

    # add info to list in memory, one by one, following signature values
    phys_resrc_ID = 1
    phys_resrc_name = "small-cavium-1"
    phys_resrc_info = "Jump server in Arm pod, 48 cores, 64G RAM, 447G SSD, aarch64 Cavium ThunderX, Ubuntu OS"
    phys_resrc_IPAddress = "10.10.50.12"
    phys_resrc_MACAddress = ""

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


def init_VNFs_Services():
    """Function to initialize VNFs and e2e Services data."""
    test_VNFs_Services = []

    # add info to list in memory, one by one, following signature values
    vnf_serv_ID = 1
    vnf_serv_name = "vCPE-1"
    vnf_serv_info = "virtual CPE in Arm pod"
    vnf_serv_IPAddress = "5.4.3.2"
    vnf_serv_URL = "http://5.4.3.2:8080"
    vnf_serv_related_phys_rsrcIDs = [2,4,6]
    vnf_serv_related_cloudvirt_rsrcIDs = [1,2]

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
    """Get all content from all binary files, and dump everything in a snapshot CSV file."""
    ## TODO
    timenow = datetime.now()


######################################################################
def main():

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

    tds = init_test_definitions()
    print(tds)
    td = get_indexed_item_from_file(1,FILE_TEST_DEFINITIONS)
    print(td)

    print()

    rcps = init_recipients()
    print(rcps)
    rcp = get_indexed_item_from_file(1,FILE_RECIPIENTS)
    print(rcp)

    print()

    challgs = init_challenge_definitions()
    print(challgs)
    chall = get_indexed_item_from_file(1,FILE_CHALLENGE_DEFINITIONS)
    print(chall)

    print()

    metricdefs = init_metric_definitions()
    print(metricdefs)

    metricdef = get_indexed_item_from_file(1,FILE_METRIC_DEFINITIONS)
    print(metricdef)
    t1 = datetime(2018,4,1,15,10,12,500000)
    t2 = datetime(2018,4,1,15,13,43,200000)
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

    ce1 = ChallengeExecution(1,"essai challenge execution",1)
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

    te1 = TestExecution(1,"essai test execution",1,1,"Gerard")
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






