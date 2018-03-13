.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. SPDX-License-Identifier CC-BY-4.0
.. (c) optionally add copywriters name

.. contents::
   :depth: 3
   :local:


================================================================
Auto User Guide: Use Case 2 Resiliency Improvements Through ONAP
================================================================

This document provides the user guide for Fraser release of Auto,
specifically for Use Case 2: Resiliency Improvements Through ONAP.


Description
===========

This use case illustrates VNF failure recovery time reduction with ONAP, thanks to its automated monitoring and management.
It simulates an underlying problem (failure, stress, etc.: any adverse condition in the network that can impact VNFs),
tracks a VNF, and measures the amount of time it takes for ONAP to restore the VNF functionality.

The benefit for NFV edge service providers is to assess what degree of added VIM+NFVI platform resilience for VNFs is obtained by
leveraging ONAP closed-loop control, vs. VIM+NFVI self-managed resilience (which may not be aware of the VNF or the corresponding
end-to-end Service, but only of underlying resources such as VMs and servers).


Preconditions:

#. hardware environment in which Edge cloud may be deployed
#. Edge cloud has been deployed and is ready for operation
#. ONAP has been deployed onto a cloud and is interfaced (i.e. provisioned for API access) to the Edge cloud
#. Components of ONAP have been deployed on the Edge cloud as necessary for specific test objectives

In future releases, Auto Use cases will also include the deployment of ONAP (if not already installed), the deployment
of test VNFs (pre-existing VNFs in pre-existing ONAP can be used in the test as well), the configuration of ONAP for
monitoring these VNFs (policies, CLAMP, DCAE), in addition to the test scripts which simulate a problem and measures recovery time.

Different types of problems can be simulated, hence the identification of multiple test cases corresponding to this use case,
as illustrated in this diagram:

.. image:: auto-UC02-testcases.jpg

Description of simulated problems/challenges:

* Physical Infra Failure

  * Migration upon host failure: Compute host power is interrupted, and affected workloads are migrated to other available hosts.
  * Migration upon disk failure: Disk volumes are unmounted, and affected workloads are migrated to other available hosts.
  * Migration upon link failure: Traffic on links is interrupted/corrupted, and affected workloads are migrated to other available hosts.
  * Migration upon NIC failure: NIC ports are disabled by host commands, and affected workloads are migrated to other available hosts.

* Virtual Infra Failure

  * OpenStack compute host service fail: Core OpenStack service processes on compute hosts are terminated, and auto-restored, or affected workloads are migrated to other available hosts.
  * SDNC service fail: Core SDNC service processes are terminated, and auto-restored.
  * OVS fail: OVS bridges are disabled, and affected workloads are migrated to other available hosts.
  * etc.

* Security

  * Host tampering: Host tampering is detected, the host is fenced, and affected workloads are migrated to other available hosts.
  * Host intrusion: Host intrusion attempts are detected, an offending workload, device, or flow is identified and fenced, and as needed affected workloads are migrated to other available hosts.
  * Network intrusion: Network intrusion attempts are detected, and an offending flow is identified and fenced.




Test execution high-level description
=====================================

The following two MSCs (Message Sequence Charts) show the actors and high-level interactions.

The first MSC shows the preparation activities (assuming the hardware, network, cloud, and ONAP have already been installed):
onboarding and deployment of VNFs (via ONAP portal and modules in sequence: SDC, VID, SO), and ONAP configuration
(policy framework, closed-loops in CLAMP, activation of DCAE).

.. image:: auto-UC02-preparation.jpg

The second MSC illustrates the pattern of all test cases for the Resiliency Improvements:
* simulate the chosen problem (a.k.a. a "Challenge") for this test case, for example suspend a VM which may be used by a VNF
* start tracking the target VNF of this test case
* measure the ONAP-orchestrated VNF Recovery Time
* then the test stops simulating the problem (for example: resume the VM that was suspended),

In parallel, the MSC also shows the sequence of events happening in ONAP, thanks to its configuration to provide Service
Assurance for the VNF.

.. image:: auto-UC02-pattern.jpg


Test design: data model, implementation modules
===============================================

The high-level design of classes shows the identification of several entities:
* Test Case: as identified above, each is a special case of the overall use case (e.g., categorized by challenge type)
* Test Definition: gathers all the information necessary to run a certain test case
* Metric Definition: describes a certain metric that may be measured, in addition to Recovery Time
* Challenge Definition: describe the challenge (problem, failure, stress, ...) simulated by the test case
* Recipient: entity that can receive commands and send responses, and that is queried by the Test Definition or Challenge Definition
(a recipient would be typically a management service, with interfaces (CLI or API) for clients to query)
* Resources: with 3 types (VNF, cloud virtual resource such as a VM, physical resource such as a server)

Three of these entities have execution-time corresponding classes:
* Test Execution, which captures all the relevant data of the execution of a Test Definition
* Challenge Execution, which captures all the relevant data of the execution of a Challenge Definition
* Metric Value, which captures the a quantitative measurement of a Metric Definition (with a timestamp)

.. image:: auto-UC02-data1.jpg

The following diagram illustrates an implementation-independent design of the attributes of these entities:
.. image:: auto-UC02-data2.jpg

This next diagram shows the Python classes and attributes, as implemented by this Use Case (for all test cases):

.. image:: auto-UC02-data3.jpg

Test definition data is stored in serialization files (Python pickles), while test execution data is stored in CSV
files, for easier post-analysis.

The module design is straightforward: functions and classes for managing data, for interfacing with recipients,
for executing tests, and for interacting with the test user (choosing a Test Definition, showing the details
of a Test Definition, starting the execution).

.. image:: auto-UC02-module1.jpg

This last diagram shows the test user menu functions:

.. image:: auto-UC02-module2.jpg

In future releases of Auto, testing environments such as FuncTest and Yardstick might be leveraged.

Also, anonymized test results could be collected from users willing to share them, and aggregates could be
maintained as benchmarks.

