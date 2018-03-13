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
"""This is the main module for OPNFV Auto Test Data for Use Case 2: Resilience Improvements Through ONAP.
Auto project: https://wiki.opnfv.org/pages/viewpage.action?pageId=12389095
"""




######################################################################
# import statements
import AutoResilGlobal
from AutoResilMgTestDef import *

# Constants 
PROJECT_NAME = "Auto"
USE_CASE_NAME = "Resilience Improvements Through ONAP"



######################################################################

def show_menu(selected_test_def_ID):
    """Show menu, with a different first line based on current Test Definition selection."""

    if selected_test_def_ID>0 :
        print("\nCurrently selected test Definition ID: ",selected_test_def_ID)
    else:
        print("\nCurrently selected test Definition ID: (none)")
    print("1: select Test Definition ID")
    print("2: view currently selected Test Definition details")
    print("3: start an execution of currently selected Test Definition")
    print("4: exit")


def get_menu_choice():
    """Get a user input (a menu entry number)."""
    while True:
        try:
            user_choice = int(input("  Choice: "))
        except ValueError:
            print("  Invalid choice (must be an integer). Try again.")
            continue
        if user_choice < 1 or user_choice > 4:
            print("  Invalid choice (must be between 1 and 4). Try again.")
            continue
        else:
            return user_choice


def get_test_def_ID():
    """Get a user input (a test definition ID)."""
    while True:
        try:
            user_test_def_ID = int(input("    Test Definition ID: "))
        except ValueError:
            print("    Invalid choice (must be an integer). Try again.")
            continue
        if user_test_def_ID <1:
            print("    Invalid choice (must be a positive integer). Try again.")
            continue
        
        test_defs = read_list_bin(FILE_TEST_DEFINITIONS)
        if (test_defs == None) or (test_defs==[]):
            print("Problem with test definition file: empty")
            sys.exit()  # stop entire program, because test definition file MUST be correct
            
        if index_already_there(user_test_def_ID, test_defs):
            return user_test_def_ID
        else:    
            print("Invalid choice (Test Definition ID",user_test_def_ID,"does not exist). Try again.")
            continue
        
    
        
######################################################################
def main():

    print("\nProject:\t", PROJECT_NAME)
    print("Use Case:\t",USE_CASE_NAME)            

            
    # Run initializations, to refresh data and make sure files are here. Also, this loads the lists in memory.
    # For now, initialization functions are self-contained and hard-coded:
    # all definition data is initialized from the code, not from user interaction.
    AutoResilGlobal.test_case_list =                init_test_cases()
    AutoResilGlobal.test_definition_list =          init_test_definitions()
    AutoResilGlobal.recipient_list =                init_recipients()
    AutoResilGlobal.challenge_definition_list =     init_challenge_definitions()
    AutoResilGlobal.metric_definition_list =        init_metric_definitions()

    AutoResilGlobal.physical_resource_list =        init_physical_resources()
    AutoResilGlobal.cloud_virtual_resource_list =   init_cloud_virtual_resources()
    AutoResilGlobal.VNF_Service_list =              init_VNFs_Services()


    # start with no test definition selected
    selected_test_def_ID = -1

    # interactive menu loop
    while True:
        
        show_menu(selected_test_def_ID)
        user_choice = get_menu_choice()
        #print("***user_choice:",user_choice) #debug
        
        if user_choice == 1:  # select Test Definition ID
            selected_test_def_ID = get_test_def_ID()
            selected_test_def = get_indexed_item_from_list(selected_test_def_ID, AutoResilGlobal.test_definition_list)
            continue

        if user_choice == 2:  # view currently selected Test Definition details
            if selected_test_def_ID > 0:
                if selected_test_def == None:
                    print("Problem with test definition: empty")
                    sys.exit()  # stop entire program, because test definition MUST be correct
                else:
                    selected_test_def.printout_all(0)
                    continue
            else:
                print("No current selection of Test Definition. Try again.")
                continue
            
        if user_choice == 3:  # start an execution of currently selected Test Definition
            if selected_test_def_ID > 0:
                if selected_test_def == None:
                    print("Problem with test definition: empty")
                    sys.exit()  # stop entire program, because test definition MUST be correct
                else:
                    # TODO run test: method of TestDefinition, or function ?
                    pass
            else:
                print("No current selection of Test Definition. Try again.")
                continue
            
        if user_choice == 4:  # exit
            print("\nEnd of Main Program")
            print("\nProject:\t", PROJECT_NAME)
            print("Use Case:\t",USE_CASE_NAME)            
            print("\nBye!\n")
            sys.exit()


    

if __name__ == "__main__":
    main()

