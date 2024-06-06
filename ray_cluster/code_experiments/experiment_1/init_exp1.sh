#!/bin/bash

###########################################################################
# Preprocess experiment
PYTHON_SCRIPT="1-exp1_ray_embl_preprocess_cluster_gs.py"

# Inference experiment
#PYTHON_SCRIPT="2-exp1_ray_embl_inference_cluster_gs.py"
###########################################################################

###########################################################################
# Cluster with 2 CPUs and 3 GB of RAM per node (1 head + 30 workers)
YAML_PATH="../../config/cluster_config/ray-cluster-2cpu-3ram.yaml"
replicas=30

# Cluster with 3 CPUs and 5 GB of RAM per node (1 head/worker + 19 workers)
#YAML_PATH="../../config/cluster_config/ray-cluster-3cpu-5ram.yaml"
#replicas=19

# Cluster with 6 CPUs and 10 GB of RAM per node (1 head/worker + 9 workers)
#YAML_PATH="../../config/cluster_config/ray-cluster-6cpu-10ram.yaml"
#replicas=9
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
sed -i "s/replicas: [0-9]\+/replicas: $replicas/" $YAML_PATH
kubectl apply -f $YAML_PATH
kubectl delete pods -l ray.io/is-ray-node=yes
wait_for_pods

# Port forwarding
kubectl port-forward --address 0.0.0.0 svc/raycluster-javi-head-svc 8265:8265 & PORT_FORWARD_PID=$!
sleep 10

# Job submit
ray job submit --address http://localhost:8265 --working-dir . -- python $PYTHON_SCRIPT

# Finish port forwarding
kill $PORT_FORWARD_PID