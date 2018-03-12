.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. SPDX-License-Identifier CC-BY-4.0
.. (c) optionally add copywriters name


================================================================
Auto User Guide: Use Case 1 Edge Cloud
================================================================

This document provides the user guide for Fraser release of Auto,
specifically for Use Case 1: Edge Cloud.
   
.. contents::
   :depth: 3
   :local:
   
   
Description
===========
   
This use case aims at showcasing the benefits of using ONAP for autonomous Edge Cloud management.

A high level of automation of VNF lifecycle event handling after launch is enabled by ONAP policies
and closed-loop controls, which take care of most lifecycle events (start, stop, scale up/down/in/out,
recovery/migration for HA) as well as their monitoring and SLA management. 

Multiple types of VNFs, for different execution environments, are first approved in the catalog thanks
to the onboarding process, and then can be deployed and handled by multiple controllers in a systematic way.

This results in management efficiency (lower control/automation overhead) and high degree of autonomy.


Preconditions:
#. hardware environment in which Edge cloud may be deployed
#. an Edge cloud has been deployed and is ready for operation
#. ONAP has been deployed onto a Cloud, and is interfaced (i.e. provisioned for API access) to the Edge cloud



Main Success Scenarios:	

* lifecycle management - stop, stop, scale (dependent upon telemetry)

* recovering from faults (detect, determine appropriate response, act); i.e. exercise closed-loop policy engine in ONAP

  * verify mechanics of control plane interaction

* collection of telemetry for machine learning


Details on the test cases corresponding to this use case:

* Environment check

  * Basic environment check: Create test script to check basic VIM (OpenStack), ONAP, and VNF are up and running

* VNF lifecycle management 

  * VNF Instance Management: Validation of VNF Instance Management which includes VNF instantiation, VNF State Management and termination

  * Tacker Monitoring Driver (VNFMonitorPing): 

    * Write Tacker Monitor driver to handle monitor_call and based on return state value create custom events
    * If Ping to VNF fails, trigger below events

      * Event 1 : Collect failure logs from VNF
      * Event 2 : Soft restart/respawn the VNF

  * Integrate with Telemetry
  
    * Create TOSCA template policies to implement ceilometer  data collection service
    * Collect CPU utilization data, compare with threshold, and perform action accordingly (respawn, scale-in/scale-out)


   
Test execution high-level description
=====================================

<TBC>

   
  

