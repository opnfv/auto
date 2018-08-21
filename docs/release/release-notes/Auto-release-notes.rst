.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. SPDX-License-Identifier CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors


Auto Release Notes
==================

This document provides the release notes for the Gambia 7.0 release of Auto.


Important notes for this release
================================

The initial release for Auto was in Fraser 6.0 (project inception: July 2017).


Summary
=======

Overview
^^^^^^^^

OPNFV is an SDNFV system integration project for open-source components, which so far have been mostly limited to
the NFVI+VIM as generally described by `ETSI <https://www.etsi.org/technologies-clusters/technologies/nfv>`_.

In particular, OPNFV has yet to integrate higher-level automation features for VNFs and end-to-end Services.

As an OPNFV project, Auto (*ONAP-Automated OPNFV*) will focus on ONAP component integration and verification with
OPNFV reference platforms/scenarios, through primarily a post-install process, in order to avoid impact to OPNFV
installer projects (Fuel/MCP, Compass4NFV, Apex/TripleO, Daisy4NFV). As much as possible, this will use a generic
installation/integration process (not specific to any OPNFV installer's technology).

* `ONAP <https://www.onap.org/>`_ (a Linux Foundation Project) is an open source software platform that delivers
  robust capabilities for the design, creation, orchestration, monitoring, and life cycle management of
  Software-Defined Networks (SDNs). The current release of ONAP is B (Beijing).

Auto aims at validating the business value of ONAP in general, but especially within an OPNFV infrastructure
(integration of ONAP and OPNFV). Business value is measured in terms of improved service quality (performance,
reliability, ...) and OPEX reduction (VNF management simplification, power consumption reduction, ...), as
demonstrated by use cases.

Auto also validates multi-architecture software (binary images and containers) availability of ONAP and OPNFV:
CPUs (x86, ARM) and Clouds (MultiVIM)

In other words, Auto is a turnkey approach to automatically deploy an integrated open-source virtual network
based on OPNFV (as infrastructure) and ONAP (as end-to-end service manager), that demonstrates business value
to end-users (IT/Telco service providers, enterprises).


While all of ONAP is in scope, as it proceeds, the Auto project will focus on specific aspects of this integration
and verification in each release. Some example topics and work items include:

* How ONAP meets VNFM standards, and interacts with VNFs from different vendors
* How ONAP SDN-C uses OPNFV existing features, e.g. NetReady, in a two-layer controller architecture in which the
  upper layer (global controller) is replaceable, and the lower layer can use different vendor’s local controller to
  interact with SDN-C. For interaction with multiple cloud infrastructures, the MultiVIM ONAP component will be used.
* How ONAP leverages OPNFV installers (Fuel/MCP, Compass4NFV, Apex/TripleO, Daisy4NFV) to provide a cloud
  instance (starting with OpenStack) on which to install the tool ONAP
* What data collection interface VNF and controllers provide to ONAP DCAE, and (through DCAE), to closed-loop control
  functions such as Policy Tests which verify interoperability of ONAP automation/lifecycle features with specific NFVI
  and VIM features, as prioritized by the project with OPNFV technical community and
  EUAG (`End User Advisory Group <https://www.opnfv.org/end-users/end-user-advisory-group>`_) input.

  Examples:

  * Abstraction of networking tech/features e.g. through NetReady/Gluon
  * Blueprint-based VNF deployment (HOT, TOSCA, YANG)
  * Application level configuration and lifecycle through YANG (for any aspects depending upon OPNFV NFVI+VIM components)
  * Policy (through DCAE)
  * Telemetry (through VES/DCAE)

Initial areas of focus for Auto (in orange dotted lines; this scope can be expanded for future releases).
It is understood that:

* ONAP scope extends beyond the lines drawn below
* ONAP architecture does not necessarily align with the ETSI NFV inspired diagrams this is based upon

.. image:: auto-proj-rn01.png


The current ONAP architecture overview can be found `here <https://onap.readthedocs.io/en/latest/guides/onap-developer/architecture/onap-architecture.html>`_.

For reference, the ONAP-Beijing architecture diagram is replicated here:

.. image:: ONAP-toplevel-beijing.png


Within OPNFV, Auto leverages tools and collaborates with other projects:

* use clouds/VIMs as installed in OPNFV infrastructure (e.g. OpenStack as installed by Fuel/MCP, Compass4NFV, etc.)
* include VNFs developed by OPNFV data plane groups (e.g., accelerated by VPP (Vector Packet Processing) with DPDK support, ...)
* validate ONAP+VNFs+VIMs on two major CPU architectures: x86 (CISC), Arm (RISC); collaborate with OPNFV/Armband
* work with other related groups in OPNFV:

  * FuncTest for software verification (CI/CD, Pass/Fail)
  * Yardstick for metric management (quantitative measurements)
  * VES (VNF Event Stream) and Barometer for VNF monitoring (feed to ONAP/DCAE)
  * Edge Cloud as use case

* leverage OPNFV tools and infrastructure:

  * Pharos as LaaS: transient pods (3-week bookings) and permanent Arm pod (6 servers)
  * `WorksOnArm <http://worksonarm.com/cluster>`_ (`GitHub link <http://github.com/worksonarm/cluster>`_)
  * possibly other labs from the community (Huawei pod-12, 6 servers, x86)
  * JJB/Jenkins for CI/CD (and follow OPNFV scenario convention)
  * Gerrit/Git for code and documents reviewing and archiving (similar to ONAP: Linux Foundation umbrella)
  * follow OPNFV releases (Releng group)


Testability
^^^^^^^^^^^

* Tests (test cases) will be developed for use cases within the project scope.
* In future releases, tests will be added to Functest runs for supporting scenarios.

Auto’s goals include the standup and tests for integrated ONAP-Cloud platforms (“Cloud” here being OPNFV “scenarios”
or other cloud environments). Thus, the artifacts would be tools to deploy ONAP (leveraging OOM whenever possible,
starting with Beijing release of ONAP, and a preference for the containerized version of ONAP), to integrate it with
clouds, to onboard and deploy test VNFs, to configure policies and closed-loop controls, and to run use-case defined
tests against that integrated environment. OPNFV scenarios would be a possible component in the above.

Installing Auto components and running a battery of tests will be automated, with some or all of the tests being
integrated in OPNFV CI/CD (depending on the execution length and resource consumption).

Combining all potential parameters, a full set of Auto test case executions can result in thousands of individual results.
The analysis of these results can be performed by humans, or even by ML/AI (Machine Learning, Artificial Intelligence).
Test results will be used to fine-tune policies and closed-loop controls configured in ONAP, for increased ONAP business
value (i.e., find/determine policies and controls which yield optimized ONAP business value metrics such as OPEX).

More precisely, the following list shows parameters that could be applied to an Auto full run of test cases:

* Auto test cases for given use cases
* OPNFV installer {Fuel/MCP, Compass4NFV, Apex/TripleO, Daisy4NFV}
* OPNFV availability scenario {HA, noHA}
* environment where ONAP runs {bare metal servers, VMs from clouds (OpenStack, AWS, GCP, Azure, ...), containers}
* ONAP installation type {bare metal, VM, or container, ...} and options {MultiVIM single|distributed, ...}
* VNF types {vFW, vCPE, vAAA, vDHCP, vDNS, vHSS, ...} and VNF-based services {vIMS, vEPC, ...}
* cloud where VNFs run {OpenStack, AWS, GCP, Azure, ...}
* VNF host type {VM, container}
* CPU architectures {x86/AMD64, ARM/aarch64} for ONAP software and for VNF software; not really important for Auto software;
* pod size and technology (RAM, storage, CPU cores/threads, NICs)
* traffic types and amounts/volumes; traffic generators (although that should not really matter);
* ONAP configuration {especially policies and closed-loop controls; monitoring types for DCAE: VES, ...}
* versions of every component {Linux OS (Ubuntu, CentOS), OPNFV release, clouds, ONAP, VNFs, ...}

The diagram below shows Auto parameters:

.. image:: auto-proj-parameters.png


The next figure is an illustration of the Auto analysis loop (design, configuration, execution, result analysis)
based on test cases covering as many parameters as possible :

.. image:: auto-proj-tests.png


Auto currently defines three use cases: Edge Cloud (UC1), Resiliency Improvements (UC2), and Enterprise vCPE (UC3). These use cases aim to show:

* increased autonomy of Edge Cloud management (automation, catalog-based deployment). This use case relates to the
  `OPNFV Edge Cloud <https://wiki.opnfv.org/display/PROJ/Edge+cloud>`_ initiative.
* increased resilience (i.e. fast VNF recovery in case of failure or problem, thanks to closed-loop control),
  including end-to-end composite services of which a Cloud Manager may not be aware (VMs or containers could be
  recovered by a Cloud Manager, but not necessarily an end-to-end service built on top of VMs or containers).
* enterprise-grade performance of vCPEs (certification during onboarding, then real-time performance assurance with
  SLAs and HA, as well as scaling).

The use cases define test cases, which initially will be independent, but which might eventually be integrated to `FuncTest <https://wiki.opnfv.org/display/functest/Opnfv+Functional+Testing>`_.

Additional use cases can be added in the future, such as vIMS (example: project `Clearwater <http://www.projectclearwater.org/>`_)
or residential vHGW (virtual Home Gateways). The interest for vHGW is to reduce overall power consumption: even in idle mode,
physical HGWs in residential premises consume a lot of energy. Virtualizing that service to the Service Provider edge data center
would allow to minimize that consumption.


Lab environment
^^^^^^^^^^^^^^^

Target architectures for all Auto use cases and test cases include x86 and Arm. Power consumption analysis will be
performed, leveraging Functest tools (based on RedFish/IPMI/ILO).

Initially, an ONAP-Amsterdam instance (without DCAE) had been installed over Kubernetes on bare metal on a single-server
x86 pod at UNH IOL.

A transition is in progress, to leverage OPNFV LaaS (Lab-as-a-Service) pods (`Pharos <https://labs.opnfv.org/>`_).
These pods can be booked for 3 weeks only (with an extension for a maximum of 2 weeks), so they are not a permanent resource.

For ONAP-Beijing, a repeatable automated installation procedure is being developed, using 3 Pharos servers (x86 for now).
Also, a more permanent ONAP installation is in progress at a Huawei lab (pod-12, consisting of 6 x86 servers,
1 as jump server, the other 5 with this example allocation: 3 for ONAP components, and 2 for an OPNFV infratructure:
Openstack installed by Compass4NFV).

ONAP-based onboarding and deployment of VNFs is in progress (ONAP-Amsterdam pre-loading of VNFs must still done outside
of ONAP: for VM-based VNFs, users need to prepare OpenStack stacks (using Heat templates), then make an instance snapshot
which serves as the binary image of the VNF).

A script to prepare an OpenStack instance for ONAP (creation of a public and a private network, with a router,
pre-loading of images and flavors, creation of a security group and an ONAP user) has been developed. It leverages
OpenStack SDK. It has a delete option, so it can be invoked to delete these objects for example in a tear-down procedure.

Integration with Arm servers has started (exploring binary compatibility):

* The Auto project has a specific 6-server pod of Arm servers, which is currently loaned to ONAP integration team,
  to build ONAP images
* A set of 14 additional Arm servers was deployed at UNH, for increased capacity
* ONAP Docker registry: ONAP-specific images for ARM are being built, with the purpose of populating ONAP nexus2
  (Maven2 artifacts) and nexus3 (Docker containers) repositories at Linux Foundation. Docker images are
  multi-architecture, and the manifest of an image may contain 1 or more layers (for example 2 layers: x86/AMD64
  and ARM/aarch64). One of ONAP-Casablanca architectural requirements is to be CPU-architecture independent.
  There are almost 150 Docker containers in a complete ONAP instance. Currently, more disk space is being added
  to the ARM nodes (configuration of Nova, and/or additional actual physical storage space).


Test case design and implementation for the three use cases has started.

OPNFV CI/CD integration with JJD (Jenkins Job Description) has started: see the Auto plan description
`here <https://wiki.opnfv.org/display/AUTO/CI+for+Auto>`_. The permanent resource for that is the 6-server Arm
pod, hosted at UNH. The CI directory from the Auto repository is `here <https://git.opnfv.org/auto/tree/ci>`_


Finally, the following figure illustrates Auto in terms of project activities:

.. image:: auto-project-activities.png


Note: a demo was delivered at the OpenStack Summit in Vancouver on May 21st 2018, to illustrate the deployment of
a WordPress application (WordPress is a platform for websites and blogs) deployed on a multi-architecture cloud (mix
of x86 and Arm servers).
This shows how service providers and enterprises can diversify their data centers with servers of different architectures,
and select architectures best suited to each use case (mapping application components to architectures: DBs,
interactive servers, number-crunching modules, ...).
This prefigures how other examples such as ONAP, VIMs, and VNFs could also be deployed on heterogeneous multi-architecture
environments (open infrastructure), orchestrated by Kubernetes. The Auto installation scripts covering all the parameters
described above could expand on that approach.

.. image:: auto-proj-openstacksummit1805.png




Release Data
============

+--------------------------------------+--------------------------------------+
| **Project**                          | Auto                                 |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | auto/opnfv-7.0.0                     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Gambia 7.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | 2018-11-02                           |
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

Initial release 6.0:

* Fraser release plan
* use case descriptions
* test case descriptions
* in-progress test case development
* lab: OPNFV and ONAP (Amsterdam) installations

Point release 6.1:

* added Gambia release plan
* started integration with CI/CD (JJB) on permanent Arm pod
* Arm demo at OpenStack Summit
* initial script for configuring OpenStack instance for ONAP, using OpenStack SDK 0.13
* initial attempts to install ONAP Beijing
* alignment with OPNFV Edge Cloud
* initial contacts with Functest

Point release 6.2:

* initial scripts for OPNFV CI/CD, registration of Jenkins slave on `Arm pod <https://build.opnfv.org/ci/view/auto/>`_
* updated script for configuring OpenStack instance for ONAP, using OpenStack SDK 0.14

Point release 7.0:

* progress on Docker registry of ONAP's Arm images
* progress on ONAP installation script for 3-server cluster of UNH servers
* CI scripts for OPNFV installers: Fuel/MCP (x86), Compass, Apex/TripleO (must run twice)
* initial CI script for Daisy4NFV (work in progress)
* JOID script, but supported only until R6.2, not Gambia 7.0
* completed script for configuring OpenStack instance for ONAP, using OpenStack SDK 0.17
* use of an additional lab resource for Auto development: 6-server x86 pod (huawei-pod12)





**JIRA TICKETS for this release:**

Dynamic online list from JIRA with filters (Fix Version = 7.0.0) and (Status = Done) :
`JIRA Auto 7.0.0. Done <https://jira.opnfv.org/browse/AUTO-50?jql=project%20%3D%20AUTO%20AND%20status%20%3D%20Done%20AND%20fixVersion%20%3D%207.0.0%20ORDER%20BY%20created%20DESC>`_

Manual selection of significant JIRA tickets for this version's highlights:

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| AUTO-37                              | Get DCAE running onto Pharos         |
|                                      | deployment                           |
+--------------------------------------+--------------------------------------+
| AUTO-42                              | Use Compass4NFV to create an         |
|                                      | OpenStack instance on a UNH pod      |
+--------------------------------------+--------------------------------------+
| AUTO-43                              | String together scripts for Fuel,    |
|                                      | Tool installation, ONAP preparation  |
+--------------------------------------+--------------------------------------+
| AUTO-44                              | Build ONAP components for arm64      |
|                                      | platform                             |
+--------------------------------------+--------------------------------------+
| AUTO-45                              | CI: Jenkins definition of verify and |
|                                      | merge jobs                           |
+--------------------------------------+--------------------------------------+
| AUTO-46                              | Use Apex to create an OpenStack      |
|                                      | instance on a UNH pod                |
+--------------------------------------+--------------------------------------+
| AUTO-47                              | Install ONAP with Kubernetes on LaaS |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| AUTO-48                              | Create documentation for ONAP        |
|                                      | deployment with Kubernetes on LaaS   |
+--------------------------------------+--------------------------------------+
| AUTO-49                              | Automate ONAP deployment with        |
|                                      | Kubernetes on LaaS                   |
+--------------------------------------+--------------------------------------+
| AUTO-51                              | huawei-pod12: Prepare IDF and PDF    |
|                                      | files                                |
+--------------------------------------+--------------------------------------+
| AUTO-52                              | Deploy a running ONAP instance on    |
|                                      | huawei-pod12                         |
+--------------------------------------+--------------------------------------+
| AUTO-54                              | Use Daisy4nfv to create an OpenStack |
|                                      | instance on a UNH pod                |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
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

7.0 release: in-progress Docker ARM images, install scripts, CI scripts, and test case implementations.


Documentation deliverables
^^^^^^^^^^^^^^^^^^^^^^^^^^

Updated versions of:

* Release Notes (this document)
* User Guide
* Configuration Guide

(see links in References section)



Known Limitations, Issues and Workarounds
=========================================

System Limitations
^^^^^^^^^^^^^^^^^^



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

For more information on the OPNFV Gambia release, please see:
http://opnfv.org/gambia


Auto Wiki pages:

* `Auto wiki main page <https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095>`_


OPNFV documentation on Auto:

* `Auto release notes <http://docs.opnfv.org/en/latest/submodules/auto/docs/release/release-notes/index.html#auto-releasenotes>`_
* `Auto use case user guides <http://docs.opnfv.org/en/latest/submodules/auto/docs/release/userguide/index.html#auto-userguide>`_
* `Auto configuration guide <http://docs.opnfv.org/en/latest/submodules/auto/docs/release/configguide/index.html#auto-configguide>`_


Git&Gerrit Auto repositories:

* `Auto Git repository <https://git.opnfv.org/auto/tree/>`_
* `Gerrit for Auto project <https://gerrit.opnfv.org/gerrit/#/admin/projects/auto>`_


Demo at OpenStack summit May 2018 (Vancouver, BC, Canada):

* YouTube video (10min 52s): `Integration testing on an OpenStack public cloud <https://youtu.be/BJ05YuusNYw>`_

