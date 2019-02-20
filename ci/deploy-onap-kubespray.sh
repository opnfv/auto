#!/bin/bash
#
# Copyright 2018-2019 Tieto
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
#       onap-deploy-kubespray.sh <MASTER> <SLAVE1> <SLAVE2>
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
LC_ALL=C
LANG=C
MASTER=$1
SERVERS=$*
shift
SLAVES=$*

BRANCH='beijing'
ENVIRON='onap'
HELM_VERSION=2.8.2

SSH_USER=${SSH_USER:-"opnfv"}
SSH_OPTIONS='-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

# by defalult install full ONAP installation
ONAP_COMPONENT_DISABLE=${ONAP_COMPONENT_DISABLE:-""}
# example of minimal ONAP installation
ONAP_COMPONENT_DISABLE="clamp cli consul dcaegen2 esr log msb multicloud nbi oof policy uui vfc vnfsdk"

# use identity file from the environment SSH_IDENTITY
if [ -n "$SSH_IDENTITY" ] ; then
    SSH_OPTIONS="-i $SSH_IDENTITY $SSH_OPTIONS"
fi

#
# Installation
#
# install K8S cluster by kubespray
apt-get -y install ansible python-jinja2 python3-pip libffi-dev libssl-dev
git clone https://github.com/kubernetes-incubator/kubespray.git
cd kubespray
pip3 install -r requirements.txt
CONFIG_FILE=inventory/auto_hosts.ini python3 contrib/inventory_builder/inventory.py $SERVERS
echo "kubelet_max_pods: 500" >> $CONFIG_FILE
cat inventory/auto_hosts.ini
ansible-playbook -i inventory/auto_hosts.ini cluster.yml

# use standalone K8S master if there are enough VMs available for the K8S cluster
SERVERS_COUNT=$(echo $SERVERS | wc -w)
if [ $SERVERS_COUNT -gt 2 ] ; then
    K8S_NODES=$SLAVES
else
    K8S_NODES=$SERVERS
fi

echo "INSTALLATION TOPOLOGY:"
echo "Kubernetes Master: $MASTER"
echo "Kubernetes Nodes: $K8S_NODES"
echo


echo "CONFIGURING NFS ON SLAVES"
echo "$SLAVES"

for SLAVE in $SLAVES;
do
ssh $SSH_OPTIONS $SSH_USER@"$SLAVE" "bash -s" <<CONFIGURENFS &
    sudo -i
    apt-get install nfs-common -y
    mkdir /dockerdata-nfs
    chmod 777 /dockerdata-nfs
    echo "$MASTER:/dockerdata-nfs /dockerdata-nfs   nfs    auto  0  0" >> /etc/fstab
    mount -a
    mount | grep dockerdata-nfs
CONFIGURENFS
done
wait

echo "DEPLOYING OOM ON MASTER"
echo "$MASTER"
TMP_POD_LIST='/tmp/onap_pod_list.txt'

ssh $SSH_OPTIONS $SSH_USER@"$MASTER" "bash -s" <<OOMDEPLOY
sudo -i
# Create $ENVIRON namespace
cat <<EOF | kubectl create -f -
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "$ENVIRON",
    "labels": {
      "name": "$ENVIRON"
    }
  }
}
EOF
kubectl get namespaces --show-labels
kubectl -n kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
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
        echo -n " \$COMPONENT"
        sed -i '/^'\${COMPONENT}':$/!b;n;s/enabled: *true/enabled: false/' onap/values.yaml
    done
    echo
fi

wget http://storage.googleapis.com/kubernetes-helm\
/helm-v${HELM_VERSION}-linux-amd64.tar.gz
tar -zxvf helm-v${HELM_VERSION}-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm
helm init --upgrade --service-account tiller
# run helm server on the background and detached from current shell
nohup helm serve  0<&- &>/dev/null &
echo "Waiting for helm setup for 5 min at \$(date)"
sleep 5m
helm version
helm repo add local http://127.0.0.1:8879
helm repo list
make all
if ( ! helm install local/onap -n dev --namespace $ENVIRON) ; then
    echo "ONAP installation has failed at \$(date)"
    exit 1
fi

cd ../../

echo "Waiting for ONAP pods to be up \$(date)"
echo "Ignore failure of sdnc-ansible-server, see SDNC-443"
function get_onap_pods() {
    kubectl get pods --namespace $ENVIRON > $TMP_POD_LIST
    return \$(cat $TMP_POD_LIST | wc -l)
}
FAILED_PODS_LIMIT=1         # maximal number of failed ONAP PODs
ALL_PODS_LIMIT=20           # minimum ONAP PODs to be up & running
WAIT_PERIOD=60              # wait period in seconds
MAX_WAIT_TIME=\$((3600*3))  # max wait time in seconds
MAX_WAIT_PERIODS=\$((\$MAX_WAIT_TIME/\$WAIT_PERIOD))
COUNTER=0
get_onap_pods
ALL_PODS=\$?
PENDING=\$(grep -E '0/|1/2' $TMP_POD_LIST | wc -l)
while [ \$PENDING -gt \$FAILED_PODS_LIMIT -o \$ALL_PODS -lt \$ALL_PODS_LIMIT ]; do
  # print header every 20th line
  if [ \$COUNTER -eq \$((\$COUNTER/20*20)) ] ; then
    printf "%-3s %-29s %-3s/%s\n" "Nr." "Datetime of check" "Err" "Total PODs"
  fi
  COUNTER=\$((\$COUNTER+1))
  printf "%3s %-29s %3s/%-3s\n" \$COUNTER "\$(date)" \$PENDING \$ALL_PODS
  sleep \$WAIT_PERIOD
  if [ "\$MAX_WAIT_PERIODS" -eq \$COUNTER ]; then
    FAILED_PODS_LIMIT=800
    ALL_PODS_LIMIT=0
  fi
  get_onap_pods
  ALL_PODS=\$?
  PENDING=\$(grep -E '0/|1/2' $TMP_POD_LIST | wc -l)
done

get_onap_pods
cp $TMP_POD_LIST ~/onap_all_pods.txt
echo
echo "========================"
echo "ONAP INSTALLATION REPORT"
echo "========================"
echo
echo "List of Failed PODs"
echo "-------------------"
grep -E '0/|1/2' $TMP_POD_LIST | tee ~/onap_failed_pods.txt
echo
echo "Summary:"
echo "--------"
echo "  PODs Failed: \$(cat ~/onap_failed_pods.txt  | wc -l)"
echo "  PODs Total:  \$(cat ~/onap_all_pods.txt  | wc -l)"
echo
echo "ONAP health TC results"
echo "----------------------"
cd oom/kubernetes/robot
./ete-k8s.sh $ENVIRON health | tee ~/onap_health.txt
echo "==============================="
echo "END OF ONAP INSTALLATION REPORT"
echo "==============================="
OOMDEPLOY

echo "Finished install, ruturned from Master at $(date)"
exit 0
