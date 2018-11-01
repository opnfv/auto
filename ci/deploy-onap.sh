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
#       2) an user account with password-less sudo access must be
#          available - default user is "opnfv"

#
# Configuration
#
DOCKER_VERSION=17.03
RANCHER_VERSION=1.6.14
RANCHER_CLI_VER=0.6.11
KUBECTL_VERSION=1.8.10
HELM_VERSION=2.8.2

MASTER=$1
SERVERS=$*
shift
SLAVES=$*

BRANCH='beijing'
ENVIRON='onap'

SSH_USER=${SSH_USER:-"opnfv"}
SSH_OPTIONS='-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
# by defalult install minimal ONAP installation
ONAP_COMPONENT_DISABLE=${ONAP_COMPONENT_DISABLE:-"clamp cli consul dcaegen2 esr log msb multicloud nbi oof policy uui vfc vnfsdk"}

# use identity file from the environment SSH_IDENTITY
if [ -n "$SSH_IDENTITY" ] ; then
    SSH_OPTIONS="-i $SSH_IDENTITY $SSH_OPTIONS"
fi

#
# Installation
#
echo "INSTALLING DOCKER ON ALL MACHINES"
echo "$SERVERS"

for MACHINE in $SERVERS;
do
ssh $SSH_OPTIONS $SSH_USER@"$MACHINE" "bash -s" <<DOCKERINSTALL &
    sudo su
    apt-get update
    curl https://releases.rancher.com/install-docker/$DOCKER_VERSION.sh | sh

    mkdir -p /etc/systemd/system/docker.service.d/
    echo "[Service]
    ExecStart=
    ExecStart=/usr/bin/dockerd -H fd:// \
    --insecure-registry=nexus3.onap.org:10001"\
     > /etc/systemd/system/docker.service.d/docker.conf

    systemctl daemon-reload
    systemctl restart docker
    apt-mark hold docker-ce

    for SERVER in $SERVERS;
    do
    echo "\$SERVER $ENVIRON\$(echo \$SERVER | cut -d. -f 4 )" >> /etc/hosts
    done

    hostname $ENVIRON\$(echo $MACHINE | cut -d. -f 4 )

    echo "DOCKER INSTALLED ON $MACHINE"
DOCKERINSTALL
done
wait

echo "INSTALLING RANCHER ON MASTER"
echo "$MASTER"

ssh $SSH_OPTIONS $SSH_USER@"$MASTER" "bash -s" <<RANCHERINSTALL &
sudo su
apt install jq -y
echo "Waiting for 30 seconds at \$(date)"
sleep 30

docker login -u docker -p docker nexus3.onap.org:10001

echo "INSTALL STARTS"
apt-get install make -y

docker run -d --restart=unless-stopped -p 8080:8080\
 --name rancher_server rancher/server:v$RANCHER_VERSION
curl -LO https://storage.googleapis.com/kubernetes-release/\
release/v$KUBECTL_VERSION/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/kubectl
mkdir ~/.kube
wget http://storage.googleapis.com/kubernetes-helm\
/helm-v${HELM_VERSION}-linux-amd64.tar.gz
tar -zxvf helm-v${HELM_VERSION}-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm

echo "Installing nfs server"
# changed from nfs_share to dockerdata-nfs
apt-get install nfs-kernel-server -y

mkdir -p /dockerdata-nfs
chmod 777 /dockerdata-nfs
echo "/dockerdata-nfs *(rw,no_root_squash,no_subtree_check)">>/etc/exports
service nfs-kernel-server restart

echo "Waiting 10 minutes for Rancher to setup at \$(date)"
sleep 600
echo "Installing RANCHER CLI, KUBERNETES ENV on RANCHER"
wget https://github.com/rancher/cli/releases/download/v${RANCHER_CLI_VER}-rc2\
/rancher-linux-amd64-v${RANCHER_CLI_VER}-rc2.tar.gz
tar -zxvf rancher-linux-amd64-v${RANCHER_CLI_VER}-rc2.tar.gz
cp rancher-v${RANCHER_CLI_VER}-rc2/rancher .

API_RESPONSE=\`curl -s 'http://127.0.0.1:8080/v2-beta/apikey'\
 -d '{"type":"apikey","accountId":"1a1","name":"autoinstall",\
 "description":"autoinstall","created":null,"kind":null,\
 "removeTime":null,"removed":null,"uuid":null}'\`
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
./rancher env create -t kubernetes $ENVIRON > kube_env_id.json
PROJECT_ID=\$(<kube_env_id.json)
echo "env id: \$PROJECT_ID"
export RANCHER_HOST_URL=http://${MASTER}:8080/v1/projects/\$PROJECT_ID
echo "you should see an additional kubernetes environment"
./rancher env ls

REG_URL_RESPONSE=\`curl -X POST -u \$KEY_PUBLIC:\$KEY_SECRET\
 -H 'Accept: application/json'\
 -H 'ContentType: application/json'\
 -d '{"name":"$MASTER"}'\
 "http://$MASTER:8080/v1/projects/\$PROJECT_ID/registrationtokens"\`
echo "REG_URL_RESPONSE: \$REG_URL_RESPONSE"
echo "Waiting for the server to finish url configuration - 1 min at \$(date)"
sleep 60
# see registrationUrl in
REGISTRATION_TOKENS=\`curl http://$MASTER:8080/v2-beta/registrationtokens\`
echo "REGISTRATION_TOKENS: \$REGISTRATION_TOKENS"
REGISTRATION_URL=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].registrationUrl\`
REGISTRATION_DOCKER=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].image\`
REGISTRATION_TOKEN=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].token\`
echo "Registering host for image: \$REGISTRATION_DOCKER\
 url: \$REGISTRATION_URL registrationToken: \$REGISTRATION_TOKEN"
HOST_REG_COMMAND=\`echo \$REGISTRATION_TOKENS | jq -r .data[0].command\`

# base64 encode the kubectl token from the auth pair
# generate this after the host is registered
KUBECTL_TOKEN=\$(echo -n 'Basic '\$(echo\
 -n "\$RANCHER_ACCESS_KEY:\$RANCHER_SECRET_KEY" | base64 -w 0) | base64 -w 0)
echo "KUBECTL_TOKEN base64 encoded: \${KUBECTL_TOKEN}"

# add kubectl config - NOTE: the following spacing has to be "exact"
# or kubectl will not connect - with a localhost:8080 error
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

echo "docker run --rm --privileged\
 -v /var/run/docker.sock:/var/run/docker.sock\
 -v /var/lib/rancher:/var/lib/rancher\
 \$REGISTRATION_DOCKER\
 \$RANCHER_URL/v1/scripts/\$REGISTRATION_TOKEN"\
 > /tmp/rancher_register_host
chown $SSH_USER /tmp/rancher_register_host

RANCHERINSTALL
wait

echo "REGISTER TOKEN"
HOSTREGTOKEN=$(ssh $SSH_OPTIONS $SSH_USER@"$MASTER" cat /tmp/rancher_register_host)
echo "$HOSTREGTOKEN"

echo "REGISTERING HOSTS WITH RANCHER ENVIRONMENT '$ENVIRON'"
echo "$SERVERS"

for MACHINE in $SERVERS;
do
ssh $SSH_OPTIONS $SSH_USER@"$MACHINE" "bash -s" <<REGISTERHOST &
    sudo su
    $HOSTREGTOKEN
    sleep 5
    echo "Host $MACHINE waiting for host registration 5 min at \$(date)"
    sleep 300
REGISTERHOST
done
wait

echo "CONFIGURING NFS ON SLAVES"
echo "$SLAVES"

for SLAVE in $SLAVES;
do
ssh $SSH_OPTIONS $SSH_USER@"$SLAVE" "bash -s" <<CONFIGURENFS &
    sudo -i
    apt update
    apt install nfs-common -y
    mkdir /dockerdata-nfs
    chmod 777 /dockerdata-nfs
    echo \"$MASTER:/dockerdata-nfs /dockerdata-nfs   nfs    auto  0  0\" >> /etc/fstab
    mount -a
    mount | grep dockerdata-nfs
CONFIGURENFS
done
wait

echo "DEPLOYING OOM ON RANCHER WITH MASTER"
echo "$MASTER"

ssh $SSH_OPTIONS $SSH_USER@"$MASTER" "bash -s" <<OOMDEPLOY &
sudo su
sysctl -w vm.max_map_count=262144
rm -rf oom
echo "pulling new oom"
git clone -b $BRANCH http://gerrit.onap.org/r/oom

# NFS FIX for aaf-locate
sed -i '/persistence:/s/^#//' ./oom/kubernetes/aaf/charts/aaf-locate/values.yaml
sed -i '/mountPath: \/dockerdata/c\    mountPath: \/dockerdata-nfs'\
 ./oom/kubernetes/aaf/charts/aaf-locate/values.yaml

echo "Pre-pulling docker images at \$(date)"
wget https://jira.onap.org/secure/attachment/11261/prepull_docker.sh
chmod 777 prepull_docker.sh
./prepull_docker.sh
echo "starting onap pods"
cd oom/kubernetes/

# Disable ONAP components
if [ -n "$ONAP_COMPONENT_DISABLE" ] ; then
    echo -n "Disable following ONAP components:"
    for COMPONENT in $ONAP_COMPONENT_DISABLE; do
        echo -n " $COMPONENT"
        sed -i '/^'${COMPONENT}':$/!b;n;s/enabled: *true/enabled: false/' onap/values.yaml
    done
    echo
fi

helm init --upgrade
helm serve &
echo "Waiting for helm setup for 5 min at \$(date)"
sleep 300
helm version
helm repo add local http://127.0.0.1:8879
helm repo list
make all
helm install local/onap -n dev --namespace $ENVIRON
cd ../../

echo "Waiting for all pods to be up for 15-80 min at \$(date)"
FAILED_PODS_LIMIT=0
MAX_WAIT_PERIODS=480 # 120 MIN
COUNTER=0
PENDING_PODS=0
while [  \$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l) \
-gt \$FAILED_PODS_LIMIT ]; do
  PENDING=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l)
  PENDING_PODS=\$PENDING
  sleep 15
  LIST_PENDING=\$(kubectl get pods --all-namespaces -o wide | grep -E '0/|1/2' )
  echo "\${LIST_PENDING}"
  echo "\${PENDING} pending > \${FAILED_PODS_LIMIT} at the \${COUNTER}th"\
       " 15 sec interval out of \${MAX_WAIT_PERIODS}"
  echo ""
  COUNTER=\$((\$COUNTER + 1 ))
  if [ "\$MAX_WAIT_PERIODS" -eq \$COUNTER ]; then
    FAILED_PODS_LIMIT=800
  fi
done

echo "Report on non-running containers"
PENDING=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2')
PENDING_COUNT=\$(kubectl get pods --all-namespaces | grep -E '0/|1/2' | wc -l)
PENDING_COUNT_AAI=\$(kubectl get pods -n $ENVIRON | grep aai- \
| grep -E '0/|1/2' | wc -l)

echo "Check filebeat 2/2 count for ELK stack logging consumption"
FILEBEAT=\$(kubectl get pods --all-namespaces -a | grep 2/)
echo "\${FILEBEAT}"
echo "sleep 5 min - to allow rest frameworks to finish at \$(date)"
sleep 300
echo "List of ONAP Modules"
LIST_ALL=\$(kubectl get pods --all-namespaces -a  --show-all )
echo "\${LIST_ALL}"
echo "run healthcheck 2 times to warm caches and frameworks"\
     "so rest endpoints report properly - see OOM-447"

echo "curl with aai cert to cloud-region PUT"
curl -X PUT https://127.0.0.1:30233/aai/v11/cloud-infrastructure/\
cloud-regions/cloud-region/CloudOwner/RegionOne \
--data "@aai-cloud-region-put.json" \
-H "authorization: Basic TW9kZWxMb2FkZXI6TW9kZWxMb2FkZXI=" \
-H "X-TransactionId:jimmy-postman" \
-H "X-FromAppId:AAI" \
-H "Content-Type:application/json" \
-H "Accept:application/json" \
--cacert aaiapisimpledemoopenecomporg_20171003.crt -k

echo "get the cloud region back"
curl -X GET https://127.0.0.1:30233/aai/v11/cloud-infrastructure/\
cloud-regions/ \
-H "authorization: Basic TW9kZWxMb2FkZXI6TW9kZWxMb2FkZXI=" \
-H "X-TransactionId:jimmy-postman" \
-H "X-FromAppId:AAI" \
-H "Content-Type:application/json" \
-H "Accept:application/json" \
--cacert aaiapisimpledemoopenecomporg_20171003.crt -k

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
