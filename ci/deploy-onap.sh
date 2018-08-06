#!/bin/bash
#
# Copyright 2018 Tieto
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script for automated deployment of ONAP with Kubernetes at OPNFV LAAS
# environment.
#
# Usage:
#       onap-deploy.sh <MASTER> <SLAVE1> <SLAVE2>
#
#   where <MASTER> and <SLAVE_IPx> are IP addresses of servers to be used
#   for ONAP installation.
#
# NOTE: Following must be assured for all MASTER and SLAVE servers before
#       onap-deploy.sh execution:
#       1) ssh access without a password
#       2) an "opnfv" user account with password-less sudo access must be
#          available

#
# Configuration
#
DOCKER_VERSION=17.03
RANCHER_VERSION=1.6.14
RANCHER_CLI_VER=0.6.11
KUBECTL_VERSION=1.8.10
HELM_VERSION=2.8.2

MASTER=$1
SERVERS=$@

BRANCH='master'
ENVIRON='onap'
APPLY_WORKAROUNDS=true
CLONE_NEW_OOM=true

#
# Installation
#
echo "INSTALLING DOCKER ON ALL MACHINES"
echo $SERVERS

for MACHINE in $SERVERS;
do
ssh opnfv@$MACHINE "bash -s" <<DOCKERINSTALL &
    sudo su
    apt-get update
    curl https://releases.rancher.com/install-docker/$DOCKER_VERSION.sh | sh

    mkdir -p /etc/systemd/system/docker.service.d/
    echo "[Service]
    ExecStart=
    ExecStart=/usr/bin/dockerd -H fd:// --insecure-registry=nexus3.onap.org:10001" > /etc/systemd/system/docker.service.d/docker.conf

    systemctl daemon-reload
    systemctl restart docker
    apt-mark hold docker-ce

    for SERVER in $SERVERS;
    do
    echo "\$SERVER $ENVIRON\$(echo \$SERVER | cut -d. -f 4 )" >> /etc/hosts
    done

    hostname $ENVIRON\$(echo $MACHINE | cut -d. -f 4 )
DOCKERINSTALL
done
wait

echo "INSTALLING RANCHER ON MASTER"
echo $MASTER

ssh opnfv@$MASTER "bash -s" <<RANCHERINSTALL &
sudo su
apt install jq -y
echo "Waiting for 30 seconds at \$(date)"
sleep 30

docker login -u docker -p docker nexus3.onap.org:10001

echo "INSTALL STARTS"
apt-get install make -y

docker run -d --restart=unless-stopped -p 8080:8080 --name rancher_server rancher/server:v$RANCHER_VERSION
curl -LO https://storage.googleapis.com/kubernetes-release/release/v$KUBECTL_VERSION/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/kubectl
mkdir ~/.kube
wget http://storage.googleapis.com/kubernetes-helm/helm-v${HELM_VERSION}-linux-amd64.tar.gz
tar -zxvf helm-v${HELM_VERSION}-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm

echo "Installing nfs server"
apt-get install nfs-kernel-server -y

mkdir -p /nfs_share
chown nobody:nogroup /nfs_share/


echo "Waiting 2 minutes for Rancher to setup at \$(date)"
sleep 120
echo "Installing RANCHER CLI, KUBERNETES ENV on RANCHER"
wget https://github.com/rancher/cli/releases/download/v${RANCHER_CLI_VER}-rc2/rancher-linux-amd64-v${RANCHER_CLI_VER}-rc2.tar.gz
tar -zxvf rancher-linux-amd64-v${RANCHER_CLI_VER}-rc2.tar.gz
cp rancher-v${RANCHER_CLI_VER}-rc2/rancher .

API_RESPONSE=\`curl -s 'http://127.0.0.1:8080/v2-beta/apikey' -d '{"type":"apikey","accountId":"1a1","name":"autoinstall","description":"autoinstall","created":null,"kind":null,"removeTime":null,"removed":null,"uuid":null}'\`
# Extract and store token
echo "API_RESPONSE: \${API_RESPONSE}"
KEY_PUBLIC=\`echo \${API_RESPONSE} | jq -r .publicValue\`
KEY_SECRET=\`echo \${API_RESPONSE} | jq -r .secretValue\`
echo "publicValue: \$KEY_PUBLIC secretValue: \$KEY_SECRET"

export RANCHER_URL=http://${MASTER}:8080
export RANCHER_ACCESS_KEY=\$KEY_PUBLIC
export RANCHER_SECRET_KEY=\$KEY_SECRET

./rancher env ls
echo "Creating kubernetes environment named ${ENVIRON}"
./rancher env delete Default
./rancher env delete $ENVIRON
./rancher env create -t kubernetes $ENVIRON > kube_env_id.json
PROJECT_ID=\$(<kube_env_id.json)
echo "env id: \$PROJECT_ID"
export RANCHER_HOST_URL=http://${MASTER}:8080/v1/projects/\$PROJECT_ID
echo "you should see an additional kubernetes environment"
./rancher env ls

REG_URL_RESPONSE=\`curl -X POST -u \$KEY_PUBLIC:\$KEY_SECRET -H 'Accept: application/json' -H 'ContentType: application/json' -d '{"name":"$MASTER"}' "http://$MASTER:8080/v1/projects/\$PROJECT_ID/registrationtokens"\`
echo "REG_URL_RESPONSE: \$REG_URL_RESPONSE"
echo "wait for server to finish url configuration - 1 min at \$(date)"
sleep 60
# see registrationUrl in
REGISTRATION_TOKENS=\`curl http://$MASTER:8080/v2-beta/registrationtokens\`
echo "REGISTRATION_TOKENS: \$REGISTRATION_TOKENS"
REGISTRATION_URL=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].registrationUrl\`
REGISTRATION_DOCKER=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].image\`
REGISTRATION_TOKEN=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].token\`
echo "Registering host for image: \$REGISTRATION_DOCKER url: \$REGISTRATION_URL registrationToken: \$REGISTRATION_TOKEN"
HOST_REG_COMMAND=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].command\`

# base64 encode the kubectl token from the auth pair
# generate this after the host is registered
KUBECTL_TOKEN=\$(echo -n 'Basic '\$(echo -n "\$RANCHER_ACCESS_KEY:\$RANCHER_SECRET_KEY" | base64 -w 0) | base64 -w 0)
echo "KUBECTL_TOKEN base64 encoded: \${KUBECTL_TOKEN}"
# add kubectl config - NOTE: the following spacing has to be "exact" or kubectl will not connect - with a localhost:8080 error
echo 'apiVersion: v1
kind: Config
clusters:
- cluster:
    api-version: v1
    insecure-skip-tls-verify: true
    server: "https://$MASTER:8080/r/projects/'\$PROJECT_ID'/kubernetes:6443"
  name: "${ENVIRON}"
contexts:
- context:
    cluster: "${ENVIRON}"
    user: "${ENVIRON}"
  name: "${ENVIRON}"
current-context: "${ENVIRON}"
users:
- name: "${ENVIRON}"
  user:
    token: "'\${KUBECTL_TOKEN}'" ' > ~/.kube/config

echo "docker run --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/rancher:/var/lib/rancher \$REGISTRATION_DOCKER \$RANCHER_URL/v1/scripts/\$REGISTRATION_TOKEN" > /tmp/rancher_register_host
chown opnfv /tmp/rancher_register_host
RANCHERINSTALL
wait

echo "REGISTER TOKEN"
HOSTREGTOKEN=$(ssh opnfv@$MASTER cat /tmp/rancher_register_host)
echo $HOSTREGTOKEN

echo "REGISTERING HOSTS WITH RANCHER ENVIRONMENT \'$ENVIRON\'"
echo $SERVERS

for MACHINE in $SERVERS;
do
ssh opnfv@$MACHINE "bash -s" <<REGISTERHOST &
    sudo su
    $HOSTREGTOKEN
    sleep 5
    echo "Host $MACHINE waiting for host registration 5 min at \$(date)"
    sleep 300
REGISTERHOST
done
wait

echo "DEPLOYING OOM ON RANCHER WITH MASTER"
echo $MASTER

ssh opnfv@$MASTER "bash -s" <<OOMDEPLOY &
sudo su
sudo sysctl -w vm.max_map_count=262144
rm -rf oom
echo "pulling new oom"
git clone -b $BRANCH http://gerrit.onap.org/r/oom

#echo "Pre-pulling docker images - 35+ min"
wget https://jira.onap.org/secure/attachment/11261/prepull_docker.sh
chmod 777 prepull_docker.sh
./prepull_docker.sh
echo "starting onap pods"
cd oom/kubernetes/
sudo helm serve &
sleep 60
helm repo add local http://127.0.0.1:8879
helm repo list
make all
sudo helm install local/onap -n dev --namespace $ENVIRON
cd ../../

echo "Waiting for all pods to be up for 15-80 min at \$(date)"
FAILED_PODS_LIMIT=0
MAX_WAIT_PERIODS=480 # 120 MIN
COUNTER=0
PENDING_PODS=0
while [  \$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l) -gt \$FAILED_PODS_LIMIT ]; do
  PENDING=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l)
  PENDING_PODS=\$PENDING
  sleep 15
  LIST_PENDING=\$(kubectl get pods --all-namespaces -o wide | grep -E '0/|1/2' )
  echo "\${LIST_PENDING}"
  echo "\${PENDING} pending > \${FAILED_PODS_LIMIT} at the \${COUNTER}th 15 sec interval"
  echo ""
  COUNTER=\$((COUNTER + 1 ))
  MAX_WAIT_PERIODS=\$((MAX_WAIT_PERIODS - 1))
  if [ "\$MAX_WAIT_PERIODS" -eq 0 ]; then
    FAILED_PODS_LIMIT=800
  fi
done

echo "Report on non-running containers"
PENDING=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2')
PENDING_COUNT=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l)
PENDING_COUNT_AAI=\$(kubectl get pods -n $ENVIRON | grep aai- | grep -E '0/|1/2' | wc -l)

echo "Check filebeat 2/2 count for ELK stack logging consumption"
FILEBEAT=\$(kubectl get pods --all-namespaces -a | grep 2/)
echo "\${FILEBEAT}"
echo "sleep 5 min - to allow rest frameworks to finish at \$(date)"
sleep 300
echo "List of ONAP Modules"
LIST_ALL=\$(kubectl get pods --all-namespaces -a  --show-all )
echo "\${LIST_ALL}"
echo "run healthcheck 2 times to warm caches and frameworks so rest endpoints report properly - see OOM-447"

echo "curl with aai cert to cloud-region PUT"
curl -X PUT https://127.0.0.1:30233/aai/v11/cloud-infrastructure/cloud-regions/cloud-region/CloudOwner/RegionOne --data "@aai-cloud-region-put.json" -H "authorization: Basic TW9kZWxMb2FkZXI6TW9kZWxMb2FkZXI=" -H "X-TransactionId:jimmy-postman" -H "X-FromAppId:AAI" -H "Content-Type:application/json" -H "Accept:application/json" --cacert aaiapisimpledemoopenecomporg_20171003.crt -k

echo "get the cloud region back"
curl -X GET https://127.0.0.1:30233/aai/v11/cloud-infrastructure/cloud-regions/ -H "authorization: Basic TW9kZWxMb2FkZXI6TW9kZWxMb2FkZXI=" -H "X-TransactionId:jimmy-postman" -H "X-FromAppId:AAI" -H "Content-Type:application/json" -H "Accept:application/json" --cacert aaiapisimpledemoopenecomporg_20171003.crt -k

# OOM-484 - robot scripts moved
cd oom/kubernetes/robot
echo "run healthcheck prep 1"
# OOM-722 adds namespace parameter
if [ "$BRANCH" == "amsterdam" ]; then
  ./ete-k8s.sh health > ~/health1.out
else
  ./ete-k8s.sh $ENVIRON health > ~/health1.out
fi
echo "sleep 5 min at \$(date)"
sleep 300
echo "run healthcheck prep 2"
if [ "$BRANCH" == "amsterdam" ]; then
  ./ete-k8s.sh health > ~/health2.out
else
  ./ete-k8s.sh $ENVIRON health > ~/health2.out
fi
echo "run healthcheck for real - wait a further 5 min at \$(date)"
sleep 300
if [ "$BRANCH" == "amsterdam" ]; then
  ./ete-k8s.sh health
else
  ./ete-k8s.sh $ENVIRON health
fi
OOMDEPLOY
wait
echo "Finished install, ruturned from Master"
exit 0
