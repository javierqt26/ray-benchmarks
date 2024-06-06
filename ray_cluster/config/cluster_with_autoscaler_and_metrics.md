# Configuración clúster de Ray con Kuberay (Ray on Kubernetes)
 
## Requisitos 
Para crear un clúster de Ray es necesario instalar Docker, Kubctl, Helm y Kind. A continuación se encuentran los comandos oficiales de instalación obtenidos de las respectivas webs.

### 1. Docker 
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
``` 
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
``` 

Es recomendable añadir al usuario al grupo docker para evitar utilizar sudo, una vez añadido se debe reiniciar el ordenador para que se apliquen los cambios.
```
sudo usermod -aG docker ${USER}
```

### 2. Kubectl
https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-kubectl-binary-with-curl-on-linux
``` 
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
``` 

### 3. Helm
https://helm.sh/docs/intro/install/#from-script
``` 
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
``` 
 
### 4. Kind
https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries
``` 
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
``` 

## Configuración
### 1. Crear un cluster de Kubernetes

```
kind create cluster --image=kindest/node:v1.23.0
```
### 2. Instalar Prometehus
Ejecutar el siguiente script [install.sh](prometheus%2Finstall.sh) que encuentra en el directorio [prometheus](prometheus) para instalar Prometheus:
```
sudo prometheus/install.sh
```

### 3. Instalar KubeRay
```
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.0-rc.0
```

### 4. Instalar RayCluster
En este paso se ha creado el fichero de configuración [ray-cluster-autoscaler-embed-grafana.yaml](cluster_config%2Fray-cluster-autoscaler-embed-grafana.yaml) que combina la utilización del autoescaler con el dashboard, Prometheus y Grafana. Con el siguiente comando se puede aplicar:
```
kubectl apply -f cluster_config/ray-cluster.autoscaler.embed-grafana.yaml
```
Una vez aplicada la configuración esperamos hasta a que se ejecuten todos los Pods, esto se puede comprobar con el siguiente comando:
```
kubectl get pod -l ray.io/node-type=head
```

### 5. Port fordward para acceder des de el PC
Ejecutar cada comando en un terminal diferente:
```
kubectl port-forward --address 0.0.0.0 raycluster-embed-grafana-head-hhwl5 8080:8080
kubectl port-forward --address 0.0.0.0 svc/raycluster-embed-grafana-head-svc 8265:8265
kubectl port-forward --address 0.0.0.0 prometheus-prometheus-kube-prometheus-prometheus-0 -n prometheus-system 9090:9090
kubectl port-forward --address 0.0.0.0 deployment/prometheus-grafana -n prometheus-system 3000:3000
```

### 6. Configurar graficas de Grafana
Una vez hecho el forward de todos los puertos podemos acceder a la interfaz web de grafana en http://localhost:3000.
Iniciamos sesión con el usuario por defecto:
``` 
admin
prom-operator
```
Añadimos los 4 gráficos del directorio [grafana_graphics](grafana_graphics) en grafana con la interfaz web: Dashboards -> Manage -> Import -> Upload JSON file -> Load

## Ejecución
Finalmente, podemos ejecutar un Ray Job con el siguiente comando, en el que se indica la direccion del clúster, los requisitos de entorno, el directorio de trabajo y el fichero a ejecutar:
```
ray job submit \
    --address http://localhost:8265 \
    --runtime-env-json='{"pip": [
        "pandas==1.5.2",
        "tqdm==4.65.0",
        "s3fs==2023.10.0",
        "pyarrow==13.0.0",
        "numpy==1.26.4",
        "torch==2.1.2",
        "torchvision==0.16.2"
    ]}' \
    --working-dir ./working_dir/ \
    -- python code.py
```
Como en este caso ya están todos los requisitos instalados se puede ejecutar el Ray Job con el siguiente comando:
```
ray job submit --address http://localhost:8265 --working-dir . -- python code.py
```

## Modificar configuración clúster
Si se quiere adaptar la configuración del clúster para aprovechar los recursos de la maquina donde se ejecuta se puede modificar el fichero [cluster_with_autoscaler_and_metrics.md](cluster_with_autoscaler_and_metrics.md) con la configuración deseada.

Para aplicar los cambios se ha de ejecutar:
```
kubectl apply -f cluster_config/ray-cluster.autoscaler.embed-grafana.yaml
kubectl delete pods -l ray.io/is-ray-node=yes
```
Es importante ejecutar de nuevo el port forwarding del dashboard, ya que al eliminar los pods se reinicia el clúster y la conexión:
``` 
kubectl port-forward --address 0.0.0.0 svc/raycluster-embed-grafana-head-svc 8265:8265
```
Finalmente, si se desea eliminar el clúster hay que ejecutar el siguiente comando:
```
kubectl delete -f cluster_config/ray-cluster.autoscaler.embed-grafana.yaml
```