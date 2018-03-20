# !/usr/bin/python
#
# Copyright (c) 2018 All rights reserved
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
import os
import re

import logging
import json
import requests

logger = logging.getLogger(__name__)

class OS_env_check:
   """Edge Clould Basic Env Function definition"""


   def __init__(self):
       """Variable Intitialization"""
       self.osver = "v2.0"
       self.imagever = "v2"
       self.keystone_ver = 'v3'
       self.tacker_ver = 'v1.0'

   def ping_os_endpoints(self):
       "Simple ping check to OpenStack endpoint"

       os_auth_url = os.environ.get('OS_AUTH_URL', None)
       password = os.environ.get('OS_PASSWORD', None)
       if os_auth_url is None:
           logger.error("Source the OpenStack credentials first")
           exit(0)
       try:
           if os_auth_url:
               endpoint_ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', os_auth_url).group()
               response = os.system("ping -c 1 " + endpoint_ip + ">/dev/null")
               if response == 0:
                  return 0
               else:
                    logger.error("Cannot talk to the OpenStack endpoint %s\n" % endpoint_ip)
                    exit(0)
       except Exception:
          logger.exception('Errors when verifying connectivity to %s', endpoint_ip)
       return False

   def fetch_token(self):
       "Fetch OS_AUTH_TOKEN from OpenStack Service"

       #url = 'http://10.164.16.100:5000/identity/v3/auth/tokens'
       url = 'http://'+self.endpoint_ip+':5000/'+self.keystone_ver+'/auth/tokens'
       data = '{"auth":{"identity":{"methods":["password"],"password":{"user":' \
              '{"domain":{"name":"default"},"name":"admin",' \
              '"password":"admin"}}},"scope":{"project":' \
              '{"domain":{"name":"default"},"name":"admin"}}}}'
       headers = {"Accept": "application/json"}
       try:
           response = requests.post(url, headers=headers,  data=data)
           header_data = (response.headers)
           token = header_data['X-Subject-Token']
           response_body = response.content
       except Exception:
           logger.error(" Failure: Not able to send API Reqest for create token")
       if (response.status_code == 201):
           response_body = response.content.decode('utf-8')
           res = json.loads(response_body)
           admin_user_id= res['token']['user']['id']
           return response.status_code,token

   def check_os_running_services(self):
       "Get active/running OpenStack Service"

       url = 'http://' + self.endpoint_ip + ':5000/' + self.keystone_ver + '/auth/tokens'
       data = '{"auth": {"identity": {"methods": ["password"],"password": \
               {"user": {"domain": {"name": "default"},"name": "admin",\
               "password": "admin"}}},\
               "scope": {"project": {"domain": {"name": "default"},"name": "admin"}}}}'
       headers = {"Accept": "application/json"}
       response = requests.post(url, headers=headers, data=data)
       service = []
       url_ep = []
       if (response.status_code == 201):
           response_body = response.content.decode('utf-8')
           res = json.loads(response_body)
           catalogs = res['token']['catalog']
           for x in catalogs:
               services = x['name']
               if x['name'] is not None:
                   service.append(x['name'])
               endpoints = x['endpoints']
               for y in endpoints:
                   url = y['url']
                   if y['url'] not in url_ep:
                      url_ep.append(url)
       return response.status_code,service,url_ep

   def check_nova_service(self, endpoints, token):
       """ checks that a simple nova operation works """

       try:
           nova_url = endpoints.get('nova')
           url = nova_url+ '/servers/detail'
           headers = {"Content-Type": "application/json", "X-Auth-Token": token}
           response = requests.get(url, headers=headers)
           if (response.status_code == 200):
              logger.info("Nova service is Active")
       except Exception as error:
           logger.error("Nova service is FAILED")
           raise error
       return response.status_code

   def check_neutron_service (self, endpoints, token):
       """ checks that a simple neutron operation works """

       try:
           neutron_url = endpoints.get('neutron')
           url = neutron_url +self.osver+'/networks'
           headers = {"Content-Type": "application/json", "X-Auth-Token": token}
           response = requests.get(url, headers=headers)
           if (response.status_code == 200):
              logger.info("Neutron service is Active")
       except Exception as error:
           logger.error("Neutron service is FAILED")
           raise error
       return response.status_code

   def check_glance_service(self, endpoints, token):
       """ checks that a simple glance operation works """

       try:
           glance_url = endpoints.get('glance')
           url = glance_url + '/' + self.imagever + '/images'
           headers = {"Content-Type": "application/json", "X-Auth-Token": token}
           response = requests.get(url, headers=headers)
           if (response.status_code == 200):
              logger.info("Glance:Image service is Active")
       except Exception as error:
           logger.error("Glance:Image service is FAILED")
           raise error
       return response.status_code

   def check_tacker_service(self, endpoints, token):
       """ checks that a simple tacker operation works """

       try:
           if 'tacker' in endpoints.keys():
               logger.info("Tacker VNF Manager service running")
           else:
               logger.error("No Tacker VNF Manager service running")
               return (0)
           tacker_url = endpoints.get('tacker')
           url = tacker_url + '/' + self.tacker_ver + '/vnf.json'
           headers = {"Content-Type": "application/json", "X-Auth-Token": token}
           response = requests.get(url, headers=headers)
           if (response.status_code == 200):
              logger.info("Tacker:VNF Manager has active VNFs")
       except Exception as error:
           logger.error("Tacker:No Active VNFs")
           raise error
       return response.status_code
