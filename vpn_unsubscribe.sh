#!/bin/sh
# test script for vpn subscribing

L3VPN = 3

AUTH = 'admin:admin'
URLTENANT = 'http://127.0.0.1:8091/v1/tenant'
URLCPE = 'http://127.0.0.1:8091/v1/cpe'
URLSTATUS = 'http://127.0.0.1:18002/resmgr/v1/dev?dev_id='
URLINTERFACE = 'http://127.0.0.1:8091/v1/cpe/interface'
URLSERVICE = 'http://127.0.0.1:8091/v1/vpn'

tenantid = 'opnfv'
tenantname = 'opnfv'

esn1 = '21500102003GH5000971'
interface1 = 'GigabitEthernet0/0/3'
vlan1 = 3006
subnet1 = '172.168.2.0'
mask2 = 24
gateway1 = '10.10.2.2'

esn2 = '2102114469P0H3000011'
interface2 = '10GE6/0/16'
vlan2 = 3000
subnet2 = '172.168.1.0'
mask2 = 24
gateway2 = '10.10.1.2'

function createtenant {

  result = curl -I -H 'Content-type:application/json' -X POST -d '{ "tenant_id": $1,
    "tenant_name":$2, "cert_type": "A", "cert_num": "000000000000000000001"}' -u $AUTH $URLTENANT
  echo 'tenant $1 is being created!'
  return result

}

function enablecpe {

  cpe_model = "4096"
  if [ $3 -eq "IMG"]; then
    cpe_model = "4098"
  fi
  if [ $3 -eq "UCPE"]; then
    cpe_model = "4096"
  fi    

  result = curl -I -H 'Content-type:application/json' -X POST -d ' { "cpe_vendor": "HUAWEI", "tenant_id": $2, "ctrler_id": "HW_AC_CAMPUS_CQ1", "access_type": 0, "cpe_model": $cpe_moel, "cpe_esn": $1 }' -u $URLCPE
  echo 'cpe $1 is being activated!'
  return result

}

function checkstatus {

  URL = {$URLSTATUS}{$1}

  result = curl -I -H "Content-type: application/json" -X GET -u $AUTH $URL
  status = jq '.status' $result
  return status

}

function cfglaninterface {

  result = curl -I -H 'Content-type:application/json' -X POST -d '{ "cpe_esn": $1, "interfaces": [ { "if_name": $2, "if_vlan": $3, "if_ip":$4, "if_mask":"24"}]  }' -u $URLINTERFACE
  echo 'cpe $1 interface $2 vlan $3 is being configured!'
  return result

}

function enablesite2site {

  result = curl -I -H 'Content-type:application/json' -X POST -d '{
    "tenant_id": $1,
    "bandwidth": 51200,
    "order_id": "20180116-16",
    "operation": 0,
    "order_name": "20180116-16",
    "internet_cfg": null,
    "vas_cfg": null,
    "vpn_config": [
        {
        "tenant_id": $1,
        "vpn_id": 1,
        "vpn_type": $L3VPN,
        "local_device": $2,
        "dl_bw": 1000,
        "ul_bw": 1000,
        "route_policy": false,
        "qos_grade": null,
        "local_type": 0,
        "local_access": {																
                "web_enable": 1,
                "dhcp_server": 1,
                "portvlan_list": [
                    
	                {
	                    "port": $3,
	                    "vlan": $4
	                }
                ],
                "subnet_list": [
			            {
			                "ipv4": $5,
			                "mask_bit": "24",
			                "gateway": "$6
			            }
                ]
            },
        "remote_device": $7,
        "remote_type": 0,
        "remote_access": {
            "dhcp_server": 1,
            "web_enable": 1,
            "portvlan_list": [
               
	                {
	                    "port": $8,
	                    "vlan": $9
	                }
            ],
            "subnet_list": [
            
			            {
			                "ipv4": $10,
			                "mask_bit": 24,
			                "gateway": $11
			            }
            ]
        }
        }
    ]
}' -u $URLSERVICE
  echo 'site2site between cpe $2 and cpe $3  is being activated for tenant $1!'
  return result

}

tenantresult = createtenant $tenantid $tenantname
if [ $tenantresult -eq 201 ]; then

  echo 'tenant opnfv has been successfully created!'

  ucperesult = enablecpe $esn1 $tenantid "UCPE"
  if [ $ucperesult -eq 201 ]; then
    echo 'cpe $esn1 has been successfully enabled!'
  elif [ $cpe1result -eq 404 ]; then
    echo 'tenant $tenantid not exits!'
  elif [ $cpe1result -eq 409 ]; then
    echo 'cpe $esn1 already exists!'
  else
    echo 'illegal result!'

  imgresult = enablecpe $esn2 $tenantid "IMG"
  if [ $imgresult -eq 201 ]; then
    echo 'cpe $esn2 has been successfully enabled!'
  elif [ $cpe2result -eq 404 ]; then
    echo 'tenant $tenantid not exits!'
  elif [ $cpe2result -eq 409 ]; then
    echo 'cpe $esn2 already exists!'
  else
    echo 'illegal result!'

  while true
  do
     sleep 30
     ucpestatus = checkstatus $esn1
     imgstatus = checkstatus $esn2
     if [ $ucpestatus -eq "Active" ] && [ $imgstatus -eq "Active"]; then
       echo 'ucpe and img are both ready for service!'
       break
     fi
  done


  ucpeinterfaceresult = cfglaninterface $esn1 $interface1 $vlan1 $ip1
  if [ $ucpeinterfaceresult -eq 200 ]; then
    echo 'cpe $esn1 interface $interface1 has been successfully configured!'
  elif [ $ucpeinterfaceresult -eq 404 ]; then
    echo 'cpe $esn1 not exits!'
  else
    echo 'illegal result!'
  
  imginterfaceresult = cfglaninterface $esn2 $interface2 $vlan2 $ip2
  if [ $imginterfaceresult -eq 200 ]; then
    echo 'cpe $esn2 interface $interface2 has been successfully configured!'
  elif [ $imginterfaceresult -eq 404 ]; then 
    echo 'cpe $esn1 not exits!'
  else 
    echo 'illegal result!'

  serviceresult = enablesite2site $tenantid $esn1 $interface1 $vlan1 $subnet1 $gateway1 $esn2 $interface2 $vlan2 $subnet2 $gateway2
  if [ $serviceresult -eq 201 ]; then
    echo 'l3vpn has been successfully enabled between cpe $esn1 and cpe $esn2!'
  elif [ $serviceresult -eq 404 ]; then 
    echo 'tenant or cpe not exits!'
  elif [ $serviceresult -eq 409 ]; then
    echo 'l3vpn already enabled!'
  elif [ $serviceresult -eq 500 ]; then
    echo $serviceresult
  else 
    echo 'illegal result!'


elif [ $result -eq 409 ]; then
  echo 'tenant already exists!'
else
  echo 'illegal result!' 
fi









