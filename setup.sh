#!/bin/bash

# Copyright 2018 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

#
# Script to build and deploy gmemegen to kubenetes
#

#
# Configurations specific to a project
#

set_constants () {
  ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" \
    -H "Metadata-Flavor: Google" | tr '/' '\n' | grep '-')
  PROJECT=$(gcloud config get-value project)
  INSTANCE_NAME="gmemegen-db"
}

install_dependencies () {
# Installs: gcloud, kubectl, docker

  curl -fsSL \
    'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' \
    | sudo apt-key add -

  sudo add-apt-repository \
    "deb https://packages.docker.com/1.12/apt/repo/ \
     ubuntu-$(lsb_release -cs) \
     main"

  sudo apt-get update
  sudo apt-get install -y docker docker-engine unzip postgresql-client-9.5 sqlite3 apache2-utils

  wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-193.0.0-linux-x86_64.tar.gz

  tar -zxf google-cloud-sdk-193.0.0-linux-x86_64.tar.gz -C ~/
  rm google-cloud-sdk-193.0.0-linux-x86_64.tar.gz

  sudo rm /usr/bin/gcloud && sudo ln -s ~/google-cloud-sdk/bin/gcloud /usr/bin/gcloud

  gcloud components install --quiet kubectl

  sudo ln -s ~/google-cloud-sdk/bin/kubectl /usr/bin/kubectl

  ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" \
    -H "Metadata-Flavor: Google" | tr '/' '\n' | grep '-')
  PROJECT=$(gcloud config get-value project)

}

build_image () {
# Build the gmemegen image

  TAG=$(date '+%s')

  IMAGE=$(sudo docker build . -t gmemegen | awk '/Successfully built/ { print $3 }')

  sudo docker tag ${IMAGE} gcr.io/${PROJECT}/gmemegen:${TAG}
}

create_kube_cluster () {
# Create a cube cluster from image
#   Requires that an image was pushed to the Container Registry

  gcloud container clusters create gmemegen --zone us-central1-f \
    --enable-autorepair --enable-autoscaling --max-nodes=10 \
    --min-nodes=1 --machine-type=n1-standard-2 --tags=memegen

  gcloud container clusters list

  # Fetching cluster endpoint and auth data.  
  gcloud container clusters get-credentials gmemegen 
    --zone us-central1-f --project ${PROJECT}

  echo "todo(sixela): specify tag, user input for key file location"
  echo "Multiple steps required to get secrets files - https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine"
  sleep 10
  # Multiple steps required to get secrets files
  #  https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine

  # Create Credentials - the 'key' file is obtained from URL link above
  kubectl create secret generic cloudsql-instance-credentials \
    --from-file=credentials.json=key

  kubectl create secret generic cloudsql-db-credentials \
    --from-literal=username=proxyuser --from-literal=password=password

  # Need to set the tag in the deployment yaml
  kubectl create -f gmemegen_deployment.yaml

  kubectl expose deployment gmemegen --type "LoadBalancer"
}

local_proxy () {
# Install cloudsql-proxy locally

  cd ~/

  if [ -f ~/cloudsql-proxy ]; then
    # Installing cloudsql-proxy 
    git clone https://github.com/GoogleCloudPlatform/cloudsql-proxy.git ~/cloudsql-proxy
  fi
  if [ ! -f ~/cloudsql-proxy/cloud_sql_proxy ]; then
    cd ~/cloudsql-proxy
    bash ~/cloudsql-proxy/download_proxy.sh
  fi

  ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" \
    -H "Metadata-Flavor: Google" | tr '/' '\n' | grep '-')
  PROJECT=$(gcloud config get-value project)
  INSTANCE_NAME="gmemegen-db"

  ~/cloudsql-proxy/./cloud_sql_proxy -dir=cloudsql -instances=${PROJECT}:${ZONE}:${INSTANCE_NAME}=tcp:5432 &

  psql -h 127.0.0.1 -U postgres

}

push_image () {
# Push the image to the Container Registry

  sudo gcloud docker -- push gcr.io/${PROJECT}/gmemegen

  gcloud container images list-tags gcr.io/${PROJECT}/gmemegen
}

run_image () {
# Run the image just created

  # Stop old image
  sudo docker stop "$(sudo docker ps | awk '/entry/ { print $1 }')"

  LATEST_IMAGE=$(sudo docker images | awk '/gcr.io/ { print $3 }' | head -1 | tr -d \n)
  echo "sudo docker run -d -p 80:80 ${LATEST_IMAGE}"
  sudo docker run -d -p 80:80 --net host ${LATEST_IMAGE}
}

while getopts ":abckipr" opt; do
  case $opt in
    a)
      # install, build and run
      install_dependencies
      set_constants
      build_image
      local_proxy
      run_image
      push_image
      ;;
    b)
      # build the image
      set_constants
      build_image
      ;;
    c)
      # Connect via proxy
      set_constants
      local_proxy
      ;;
    i)
      # install dependencies
      install_dependencies
      set_constants
      ;;
    k)
      # create kuberenetes cluster
      set_constants
      create_kube_cluster
      ;;
    p)
      # push to Container Registry
      set_constants
      push_image
      ;;
    r)
      # run the image
      run_image
      ;;
    \?)
      echo "Invalid option: -$OPTARG"
      # todo(): call help menu
      ;;
  esac
done
