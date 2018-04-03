"""Script to Test the AUTO Edge Cloud OpenStack Services."""
# !/usr/bin/python
#
# Copyright (c) 2018 All rights reserved
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#fetch_token
# http://www.apache.org/licenses/LICENSE-2.0
#
# ###########################################################################
#                          OPNFV AUTO Edge Cloud Script
# **** Scripted by Mohankumar Navaneethan  - mnavaneethan@mvista.com ******
# ###########################################################################

# Testcase 1 : Ping OpenStack Endpoints
# Testcase 2 : Creation of Auth-Token
# TestCase 3 : Check OpenStack Active Services
# TestCase 4 : Check OpenStack Nova Service
# TestCase 5 : Check OpenStack Neutron Service
# TestCase 6 : Check OpenStack Glance Service
# TestCase 7 : Check OpenStack Tacker Service.
# ###########################################################################
#
import logging
from AutoOSPlatCheck import OS_env_check


class Env_check:
    """Script to Test AUTO Edge Cloud OpenStack Services."""
    logger = logging.getLogger(__name__)
    Env_obj = OS_env_check()
    print("################################################################")
    print("                    OPNFV AUTO Script             ")
    print("################################################################")
    logger.info("Prerequisites OpenStack configuration for AUTO")
    #########################################################################
    logger.info("\t1. Ping OpenStack Endpoints")
    if (Env_obj.ping_endpoints == 0):
        logger.info("\t\tPing to OpenStack Endpoint is successfull")
    else:
        logger.error("\t\tPing to OpenStack Endpoint is NOT successfull")

    logger.info("\t2. Creation of Auth-Token")
    response_code , token = Env_obj.fetch_token()
    if (response_code == 201):
        logger.info("\t\tCreation of Token is successfull")
    else:
        logger.error("\t\t  :  Creation of Token is NOT successfull")
    logger.info("\t3. Check OpenStack Active Services")
    status, services, endpoint = Env_obj.check_os_running_services()
    endpoints = dict(zip(services, endpoint))
    if (status == 201):
        logger.info("\t\tCheck OpenStack Active Services is successfull")
    else:
        logger.error("\t\tCheck OpenStack Active Services is NOT successfull")

    logger.info("\t4. Check OpenStack Nova Service")
    if (Env_obj.check_nova_service(endpoints, token) == 200):
        logger.info("\t\tNova service is responsive")
    else:
        logger.error("\t\tNova service is NOT responsive")

    logger.info("\t5. Check OpenStack Neutron Service")
    if (Env_obj.check_neutron_service(endpoints, token) == 200):
        logger.info("\t\tNeutron service is responsive")
    else:
        logger.error("\t\tNeutron service is NOT responsive")

    logger.info("\t6. Check OpenStack Glance Service")
    if (Env_obj.check_glance_service(endpoints, token) == 200):
        logger.info("\t\tGlance service is responsive")
    else:
        logger.error("\t\tGlance service is NOT responsive")

    logger.info("\t7. Check OpenStack Tacker Service")
    if (Env_obj.check_glance_service(endpoints, token) == 200):
        logger.info("\t\tTacker VNF Manager service is responsive")
    else:
        logger.error("\t\tTacker VNF Manager is NOT responsive")
