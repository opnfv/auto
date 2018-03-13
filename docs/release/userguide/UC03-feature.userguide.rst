.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. SPDX-License-Identifier CC-BY-4.0
.. (c) optionally add copywriters name

.. contents::
   :depth: 3
   :local:


===========================================
Auto User Guide: Use Case 3 Enterprise vCPE
===========================================

This document provides the user guide for Fraser release of Auto,
specifically for Use Case 3: Enterprise vCPE.


Description
===========

This Use Case shows how ONAP can help ensuring that virtual CPEs (including vFW: virtual firewalls) in Edge Cloud are enterprise-grade.

ONAP operations include a verification process for VNF onboarding (i.e. inclusion in the ONAP catalog),
with multiple Roles (designer, tester, governor, operator), responsible for approving proposed VNFs
(as VSPs (Vendor Software Products), and eventually as end-to-end Services).

This process guarantees a minimum level of quality of onboarded VNFs. If all deployed vCPEs are only
chosen from such an approved ONAP catalog, the resulting deployed end-to-end vCPE services will meet
enterprise-grade requirements. ONAP provides a NBI in addition to a standard portal, thus enabling
a programmatic deployment of VNFs, still conforming to ONAP processes.

Moreover, ONAP also comprises real-time monitoring (by the DCAE component), which monitors performance for SLAs,
can adjust allocated resources accordingly (elastic adjustment at VNF level), and can ensure High Availability.

DCAE executes directives coming from policies described in the Policy Framework, and closed-loop controls
described in the CLAMP component.

Finally, this automated approach also reduces costs, since repetitive actions are designed once and executed multiple times,
as vCPEs are instantiated and decommissioned (frequent events, given the variability of business activity,
and a Small Business market similar to the Residential market: many contract updates resulting in many vCPE changes).

NFV edge service providers need to provide site2site, site2dc (Data Center) and site2internet services to tenants
both efficiently and safely, by deploying such qualified enterprise-grade vCPE.


Preconditions:

#. hardware environment in which Edge cloud may be deployed
#. an Edge cloud has been deployed and is ready for operation
#. enterprise edge devices, such as ThinCPE, have access to the Edge cloud with WAN interfaces
#. ONAP components (MSO, SDN-C, APP-C and VNFM) have been deployed onto a cloud and are interfaced (i.e. provisioned for API access) to the Edge cloud


Main Success Scenarios:

* VNF spin-up

  * vCPE spin-up: MSO calls the VNFM to spin up a vCPE instance from the catalog and then updates the active VNF list
  * vFW spin-up: MSO calls the VNFM to spin up a vFW instance from the catalog and then updates the active VNF list

* site2site

  * L3VPN service subscribing: MSO calls the SDNC to create VXLAN tunnels to carry L2 traffic between client's ThinCPE and SP's vCPE, and enables vCPE to route between different sites.
  * L3VPN service unsubscribing: MSO calls the SDNC to destroy tunnels and routes, thus disable traffic between different sites.


See `ONAP description of vCPE use case <https://wiki.onap.org/display/DW/Use+Case+proposal%3A+Enterprise+vCPE>`_ for more details, including MSCs.


Details on the test cases corresponding to this use case:

* VNF Management

  * Spin up a vCPE instance: Spin up a vCPE instance, by calling NBI of the orchestrator.
  * Spin up a vFW instance: Spin up a vFW instance, by calling NBI of the orchestrator.

* VPN as a Service
  * Subscribe to a VPN service: Subscribe to a VPN service, by calling NBI of the orchestrator.
  * Unsubscribe to a VPN service: Unsubscribe to a VPN service, by calling NBI of the orchestrator.

* Internet as a Service

  * Subscribe to an Internet service: Subscribe to an Internet service, by calling NBI of the orchestrator.
  * Unsubscribe to an Internet service: Unsubscribe to an Internet service, by calling NBI of the orchestrator.


Test execution high-level description
=====================================

<TBC>

