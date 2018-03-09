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

# This module: main program
# data initialization
# interactive CLI user menu:
# 1) select a test definition to run
# 2) view definition of selected test (pull all data from definition files)
# 3) start test
# 4) exit


#docstring
""" This is the main module for OPNFV Auto Test Data for Use Case 2: Resilience Improvements Through ONAP.
Auto project: https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095
"""




######################################################################
# import statements
from AutoResilMgTestDef import *

# Constants 
PROJECT_NAME = "Auto"
USE_CASE_NAME = "Resilience Improvements Through ONAP"


######################################################################

def show_menu(selected_test_def_ID):
    print("Project ", PROJECT_NAME, ", Use Case: ",USE_CASE_NAME)
    if selected_test_def_ID>0 :
        print("Current test Definition ID: ",selected_test_def_ID)
    else:
        print("Current test Definition ID: (none)")
    print("1: select Test Definition ID")
    print("2: view current Test Definition details")
    print("3: start an execution of current Test Definition")
    print("4: exit")


def get_menu_choice():

    while True:
        try:
            user_choice = int(input("  Choice: "))
        except ValueError:
            print("Invalid choice (must be an integer). Try again.")
            continue
        if user_choice < 1 or user_choice > 4:
            print("Invalid choice (must be between 1 and 4). Try again.")
            continue
        else:
            return user_choice


def get_test_def_ID():

    while True:
        try:
            user_test_def_ID = int(input("  Test Definition ID: "))
        except ValueError:
            print("Invalid choice (must be an integer). Try again.")
            continue

        test_defs = read_list_bin(FILE_TEST_DEFINITIONS)
        if (test_defs == None) or (test_defs==[]):
            print("Problem with test definition file: empty")
            sys.exit()
            
        if index_already_there(user_test_def_ID, test_defs):
            return user_test_def_ID
        else:    
            print("Invalid choice (Test Definition ID ",user_test_def_ID," does not exist). Try again.")
            continue
        
    
        
######################################################################
def main():

    # TODO: run initializations to refresh data and make sure files are here

    selected_test_def_ID = -1

    while True:
        
        show_menu(selected_test_def_ID)
        user_choice = get_menu_choice()
        #print("user_choice:",user_choice) #test
        
        if user_choice == 1:
            selected_test_def_ID = get_test_def_ID()
            
        if user_choice == 4:
            sys.exit()
    
    print(get_indexed_item_from_file(selected_test_def_ID,FILE_TEST_DEFINTIONS))

    print(get_indexed_item_from_file(5,FILE_TEST_CASES))
    
    print("End of Main\n  Project: \t\t", PROJECT_NAME, "\n  Use Case:\t",USE_CASE_NAME)

if __name__ == "__main__":
    main()

