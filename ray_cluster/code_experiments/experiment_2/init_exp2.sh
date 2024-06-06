#!/bin/bash

PYTHON_SCRIPT="1-exp2_ray_embl_inference_cluster_gs.py"

###########################################################################
# Cluster with 2 CPUs and 3 GB of RAM per node
YAML_PATH="../../config/cluster_config/ray-cluster-2cpu-3ram.yaml"
min_replicas=1
max_replicas=60
concurrency=$min_replicas

# Cluster with 3 CPUs and 5 GB of RAM per node
#YAML_PATH="../../config/cluster_config/ray-cluster-3cpu-5ram.yaml"
#min_replicas=0
#max_replicas=39
#concurrency=$((min_replicas + 1))


# Cluster with 6 CPUs and 10 GB of RAM per node
#YAML_PATH="../../config/cluster_config/ray-cluster-6cpu-10ram.yaml"
#min_replicas=0
#max_replicas=19
#concurrency=$((min_replicas + 1))
###########################################################################

wait_for_pods() {
  while true; do
    STATUS=$(kubectl get pods -l ray.io/is-ray-node=yes -o jsonpath='{.items[*].status.phase}')
    if [[ "$STATUS" == *"Pending"* ]] || [[ "$STATUS" == *"ContainerCreating"* ]]; then
      echo "Waiting for the pods to be in Running state..."
      sleep 10
    else
      echo "All pods are in Running state."
      break
    fi
  done
}

# Create cluster
sed -i "s/replicas: [0-9]\+/replicas: $min_replicas/" $YAML_PATH
kubectl apply -f $YAML_PATH
kubectl delete pods -l ray.io/is-ray-node=yes
wait_for_pods

# Port forwarding
kubectl port-forward --address 0.0.0.0 svc/raycluster-javi-head-svc 8265:8265 & PORT_FORWARD_PID=$!
sleep 10

for ((replicas=$min_replicas; replicas<max_replicas; replicas++))
do
  sed -i "s/replicas: [0-9]\+/replicas: $replicas/" $YAML_PATH
  kubectl apply -f $YAML_PATH
  wait_for_pods
  ray job submit --address http://localhost:8265 --working-dir . -- python $PYTHON_SCRIPT "$concurrency"
  ((concurrency++))
done

# Finish port forwarding
kill $PORT_FORWARD_PID