#!/usr/bin/env python3

# OPNFV Auto project
# https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095

# (c) by Gerard Damm (Wipro)
# Use case group: Resilience Improvements
# this module: main program

#docstring
"""
This is the main module for OPNFV Auto Test Data for Use Caes 2: Resilience Improvements Through ONAP.
"""

######################################################################
# import statements
from AutoResilMgTestDef import *

# Constants 
PROJECT = "Auto"
USE_CASE_GROUP = "Resilience Improvements Through ONAP"


######################################################################
def main():

    print(get_test_case(5))
    
    print("End of Main\n  Project: \t\t", PROJECT, "\n  Use Case Group:\t",USE_CASE_GROUP)

if __name__ == "__main__":
    main()

