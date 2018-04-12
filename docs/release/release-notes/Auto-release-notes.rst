.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. SPDX-License-Identifier CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors


Auto Release Notes
==================

This document provides the release notes for Fraser release of Auto.


Important notes for this release
================================

Initial release (project inception: July 2017).


Summary
=======

OPNFV is a SDNFV system integration project for open-source components, which so far have been mostly limited to the NFVI+VIM as generally described by ETSI.

In particular, OPNFV has yet to integrate higher-level automation features for VNFs and end-to-end Services.

Auto ("ONAP-Automated OPNFV") will focus on ONAP component integration and verification with OPNFV reference platforms/scenarios, through primarily a post-install process in order to avoid impact to OPNFV installer projects. As much as possible, this will use a generic installation/integration process (not specific to any OPNFV installer's technology).

* `ONAP <https://www.onap.org/>`_ (a Linux Foundation Project) is an open source software platform that delivers robust capabilities for the design, creation, orchestration, monitoring, and life cycle management of Software-Defined Networks (SDNs).

While all of ONAP is in scope, as it proceeds, the project will focus on specific aspects of this integration and verification in each release. Some example topics and work items include:

* How ONAP meets VNFM standards, and interacts with VNFs from different vendors
* How ONAP SDN-C uses OPNFV existing features, e.g. NetReady, in a two-layer controller architecture in which the upper layer (global controller) is replaceable, and the lower layer can use different vendor’s local controller to interact with SDN-C
* What data collection interface VNF and controllers provide to ONAP DCAE, and (through DCAE), to closed-loop control functions such as Policy Tests which verify interoperability of ONAP automation/lifecycle features with specific NFVI and VIM features, as prioritized by the project with technical community and EUAG input. Examples include:

  * Abstraction of networking tech/features e.g. through NetReady/Gluon
  * Blueprint-based VNF deployment (HOT, TOSCA, YANG)
  * Application level configuration and lifecycle through YANG (for any aspects depending upon OPNFV NFVI+VIM components)
  * Policy (through DCAE)
  * Telemetry (through VES/DCAE)

Initial areas of focus for Auto (in orange dotted lines; this scope can be expanded for future releases). It is understood that:

* ONAP scope extends beyond the lines drawn below
* ONAP architecture does not necessarily align with the ETSI NFV inspired diagrams this is based upon

.. image:: auto-proj-rn01.png


Testability:

* Tests will be developed for use cases within the project scope.
* In future releases, tests will be added to Functest runs for supporting scenarios.

Auto’s goals include the standup and tests for integrated ONAP-Cloud platforms (“Cloud” here being OPNFV “scenarios” or other cloud environments). Thus, the artifacts would be tools to deploy ONAP (leveraging OOM whenever possible (starting with Beijing release of ONAP), and a preference for the containerized version of ONAP), to integrate it with clouds, to onboard and deploy test VNFs, to configure policies and closed-loop controls, and to run use-case defined tests against that integrated environment. OPNFV scenarios would be a possible component in the above.

Auto currently defines three use cases: Edge Cloud, Resiliency Improvements, and Enterprise vCPE. These use cases aim to show:

* increased autonomy of Edge Cloud management (automation, catalog-based deployment)
* increased resilience (i.e. fast VNF recovery in case of failure or problem, thanks to closed-loop control), including end-to-end composite services of which a Cloud Manager may not be aware
* enterprise-grade performance of vCPEs (certification during onboarding, then real-time performance assurance with SLAs and HA as well as scaling).

The use cases define test cases, which initially will be independent, but which might eventually be integrated to FuncTest.

Additional use cases can be added in the future, such as vIMS (example: project Clearwater).

Target architectures include x86 and Arm.

An ONAP instance (without DCAE) has been installed over Kubernetes on bare metal on an x86 pod of 6 servers at UNH IOL. A transition is in progress, to leverage OPNFV LaaS (Lab-as-a-Service) pods (`Pharos <https://labs.opnfv.org/>`_).
ONAP-based onboarding and deployment of VNFs is in progress (ONAP pre-loading of VNFs must still done outside of ONAP: for VM-based VNFs, need to prepare OpenStack stacks (using Heat templates), then make an instance snapshot which serves as the binary image of the VNF).

Integration with Arm servers has started (exploring binary compatibility):

* Openstack is currently installed on a 6-server pod of Arm servers
* A set of 14 additional Arm servers was deployed at UNH, for increased capacity
* Arm-compatible Docker images are in the process of being developed

Test case implementation for the three use cases has started.

Finally, the following figure illustrates Auto in terms of project activities:

.. image:: auto-project-activities.png



Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | Fraser/auto/auto@opnfv               |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Fraser 6.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2018-04-20                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Official OPNFV release               |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Version change
^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~
- There have been no version changes.


Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~
- There have been no version changes.


Reason for version
^^^^^^^^^^^^^^^^^^

Feature additions
~~~~~~~~~~~~~~~~~

Initial release, with use case descriptions, release plan, and in-progress test cases and ONAP installations.


**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| AUTO-1, UC1 definition               | Define Auto-UC-01 Service Provider's |
|                                      | Management of Edge Cloud             |
+--------------------------------------+--------------------------------------+
| AUTO-2, UC2 definition               | Define Auto-UC-02 Resilience         |
|                                      | Improvements through ONAP            |
+--------------------------------------+--------------------------------------+
| AUTO-7, UC3 definition               | Define Auto-UC-03 Enterprise vCPE    |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| AUTO-4, UC2 test case definition     | Develop test cases for Auto-UC-02    |
|                                      | Resilience Improvements through ONAP |
+--------------------------------------+--------------------------------------+
| AUTO-8, UC3 test case definition     | Develop test cases for Auto-UC-03    |
|                                      | Enterprise vCPE                      |
+--------------------------------------+--------------------------------------+
| (UC1 test case definition is done,   |                                      |
|  but no associated JIRA ticket)      |                                      |
+--------------------------------------+--------------------------------------+
| AUTO-5, install ONAP                 | Getting ONAP running onto Pharos     |
|                                      | deployment (without DCAE)            |
+--------------------------------------+--------------------------------------+
| AUTO-31, UC1 test case progress      | auto-edge-pif-001 Basic OpenStack    |
|                                      | environment check                    |
+--------------------------------------+--------------------------------------+
| AUTO-13, UC2 test case progress      | Develop test script for vif-001:     |
|                                      | Data Management                      |
+--------------------------------------+--------------------------------------+
| AUTO-20, UC3 test case progress      | Onboarding of VNFs via SDC GUI       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+



Bug corrections
~~~~~~~~~~~~~~~

**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+


Deliverables
============

Software deliverables
^^^^^^^^^^^^^^^^^^^^^

Initial release: in-progress install scripts and test case implementations.


Documentation deliverables
^^^^^^^^^^^^^^^^^^^^^^^^^^

Initial versions of:

* Release notes (this document)
* User guide `OPNFV User and Configuration Guide <http://docs.opnfv.org/en/latest/release/userguide.introduction.html>`_
* Configuration Guide (same landing page as User Guide)




Known Limitations, Issues and Workarounds
=========================================

System Limitations
^^^^^^^^^^^^^^^^^^

* ONAP still to be validated for Arm servers
* DCAE still to be validated for Kubernetes



Known issues
^^^^^^^^^^^^

None at this point.


**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Workarounds
^^^^^^^^^^^

None at this point.



Test Result
===========

None at this point.



+--------------------------------------+--------------------------------------+
| **TEST-SUITE**                       | **Results:**                         |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

References
==========

For more information on the OPNFV Fraser release, please see:
http://opnfv.org/fraser


Auto Wiki pages:

* `Auto wiki main page <https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095>`_


OPNFV documentation on Auto:

* `Auto release notes <http://docs.opnfv.org/en/latest/release/release-notes.html>`_
* `Auto use case user guides <http://docs.opnfv.org/en/latest/submodules/auto/docs/release/userguide/index.html#auto-userguide>`_
* `Auto configuration guide <http://docs.opnfv.org/en/latest/submodules/auto/docs/release/configguide/index.html#auto-configguide>`_


Git&Gerrit Auto repositories:

* `Auto Git repository <https://git.opnfv.org/auto/tree/>`_
* `Gerrit for Auto project <https://gerrit.opnfv.org/gerrit/#/admin/projects/auto>`_



