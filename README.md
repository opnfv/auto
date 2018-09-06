Auto
====

#### Recent Changes ####
- Outdated
- Add util modules for common use in project
- Add scripts to setup ONAP (Currently only on OpenStack)


#### Current Code Structure ####

    ├── auto # Auto modules
    │   ├── __init__.py
    │   └── util # util modules
    │       ├── __init__.py
    │       ├── openstack_lib.py
    │       ├── util.py
    │       └── yaml_type.py
    ├── prepare.sh # prepare virtual env, install Auto modules
    ├── requirements.txt
    ├── setup # scripts to setup ONAP
    │   └── onap_on_openstack # set ONAP on OpenStack using heat
    │       ├── config.yml
    │       ├── __init__.py
    │       ├── launch_onap.py
    │       └── onap_os_builder.py
    └── setup.py # setup Auto modules

#### Setup ONAP ####
A working ONAP environment is required before other test activity aiming for ONAP can be carried out.

**Usage**:

1. run command:

        bash prepare.sh
2. configure setup/onap_on_openstack/config.yml
3. under setup/onap_on_openstack/ run command:

        python launch_onap.py -c config.yml
