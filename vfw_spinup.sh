#!/bin/sh
# spin up a new vfw instance

URLSPINUP = 'http://127.0.0.1:18003/vnf/v1'
URLSTATUS = 'http://127.0.0.1:18002/resmgr/v1/dev?dev_id='
AUTH = 'admin:admin'

dev_id = "0488033DDN20180118150535B7F76420"
vnf_name = "vfw_20180118150535"
esn = "0488033DDN20180118150535B7F76420"

function spinup {

  result = curl -I -H "Content-type: application/json" -X POST -u $AUTH -d '{ "dev_id": $1, "vnf_name": $2, "ctrler_id": "HW_AC_CAMPUS_CQ2", "vnfm_id": "HW_VNFM_CQ", "dev_vendor": "HUAWEI", "dev_model": "VNFM", "vnf_type": "VFW", "vnf_esn": $3, "netconf_cfg": { "ipv4": "192.168.20.129", "mask_bit": 24, "ipv4_gw": "192.168.20.254"}, "wan_cfg": {"ipv4": "192.168.40.40", "mask_bit": 24, "ipv4_gw": "192.168.40.254"}, "status": "Active" }' $URLSPINUP
  echo 'trying to spin up a new vfw instance'
  return result

}

function checkstatus {

  URL = {$URLSTATUS}{$1}

  result = curl -I -H "Content-type: application/json" -X GET -u $AUTH $URL
  status = jq '.status' $result
  return status    

}

data = json
result = sinup $dev_id $vnf_name $esn 

if [ $result -eq 200 ]; then
  
  echo 'vfw is being spinned up, wait...'
  
  while true
  do
     sleep 30
     status = checkstatus $dev_id
     if [ $status -eq "Active" ]; then
       echo 'vfw is active now!'
       break
  done
  
elif [ $result -gt 300 ]; then
  echo 'error happens!'
else
  echo 'illegal json result!'
fi



