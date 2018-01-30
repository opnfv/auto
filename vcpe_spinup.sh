#!/bin/sh
# spin up a new vcpe instance

URLSPINUP = 'http://127.0.0.1:18003/vnf/v1'
URLSTATUS = 'http://127.0.0.1:18002/resmgr/v1/dev?dev_id='

URLINTF = 'http://127.0.0.1:18002/resmgr/v1/dev/if'
URLINTFCONF = 'http://127.0.0.1:18002/ifconfig/v1'
URLROUTE = 'http://127.0.0.1:18002/rtconfig/v1'

AUTH = 'admin:admin'

dev_id = "2188032VRE2018011814131903B81436"
vnf_name = "vcpe_20180118150535"
esn = "2188032VRE2018011814131903B81436"

function spinup {

  result = curl -I -H "Content-type: application/json" -X POST -u $AUTH -d '{ "dev_id": $1, "vnf_name": $2, "ctrler_id": "HW_AC_CAMPUS_CQ2", "vnfm_id": "HW_VNFM_CQ", "dev_vendor": "HUAWEI", "dev_model": "VNFM", "vnf_type": "VCPE", "vnf_esn": $3, "netconf_cfg": { "ipv4": "172.17.11.122", "ipv4_gw": "172.17.11.1"}, "status": "Active" }' $URLSPINUP
  echo 'trying to spin up a new vcpe instance'
  return result

}

function checkstatus {

  URL = {$URLSTATUS}{$1}

  result = curl -I -H "Content-type: application/json" -X GET -u $AUTH $URL
  status = jq '.status' $result
  return status    

}

function cfgwaninterface {

  result = curl -I -H "Content-type: application/json" -X POST -u $AUTH -d '{"dev_id": $1, "if_name": $2, "if_lable": "WAN", "access_ipv4": "192.168.40.30"}' $URLINTF
  
  if [ $result -eq 200]; then  

    result = curl -I -H "Content-type: application/json" -X POST -u $AUTH -d '{"dev_id": $1, "if_name": $2, "ip_cfg": {"ip":$3, "gateway": $4} }' $URLINTFCONF
    return result

  else
    return result
  
  fi

}

function cfgdefaultroute {

  result = curl -I -H "Content-type: application/json" -X POST -u $AUTH -d '{"dev_id": $1, "static_rt": {"dst":"0.0.0.0/0", "nexthop": $2} }' $URLROUTE
  return result

}

function enablewan {

   result = cfgwaninterface $1 $2 $3 $4
   if [ $result -eq 200]; then
     result = cfgdefaultroute $1 $4
     return result
   else
     return result
   fi

}

data = json
result = sinup $dev_id $vnf_name $esn 

if [ $result -eq 200 ]; then
  
  echo 'vcpe is being spinned up, wait...'
  
  while true
  do
     sleep 30
     status = checkstatus $dev_id
     if [ $status -eq "Active" ]; then
       echo 'vcpe is active now!'
       break
     fi
  done

  result = enablewan $dev_id "GigabitEthernet0/0/1" "192.168.40.30" "192.168.40.254"
  if [ $result -eq 200]; then
    echo 'vcpe is ready for service!'
  fi
  
elif [ $result -gt 300 ]; then
  echo 'error happens!'
else
  echo 'illegal json result!'
fi



