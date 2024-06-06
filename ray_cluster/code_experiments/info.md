## Ejecución de los experimentos

### Experimento 1
El script [init_exp1.sh](experiment_1%2Finit_exp1.sh) permite la ejecución automática.

En función de si el experimento es de preprocesamiento o inferencia se debe descomentar una linea o otra en [init_exp1.sh](experiment_1%2Finit_exp1.sh).

En función del clúster en que se desea ejecutar las pruebas hay que descomentar unas lineas o otras, ya que los parámetros cambian en función de los recursos. Se debe de realizar tanto en el script [init_exp1.sh](experiment_1%2Finit_exp1.sh) como en el código [1-exp1_ray_embl_preprocess_cluster_gs.py](experiment_1%2F1-exp1_ray_embl_preprocess_cluster_gs.py) o [2-exp1_ray_embl_inference_cluster_gs.py](experiment_1%2F2-exp1_ray_embl_inference_cluster_gs.py).

### Experimento 2
El script [init_exp2.sh](experiment_2%2Finit_exp2.sh) permite la ejecución automática.

En función del clúster en que se desea ejecutar las pruebas hay que descomentar unas lineas o otras. Se debe de realizar tanto en el script [init_exp2.sh](experiment_2%2Finit_exp2.sh) como en el código [1-exp2_ray_embl_inference_cluster_gs.py](experiment_2%2F1-exp2_ray_embl_inference_cluster_gs.py).

### Experimento 3
La ejecución de este experimento es manual. Ajustar las replicas del clúster [ray-cluster-autoscaler.yaml](..%2Fconfig%2Fcluster_config%2Fray-cluster-autoscaler.yaml) y la concurrencia del código [1-exp3_ray_embl_inference_cluster.py](experiment_3%2F1-exp3_ray_embl_inference_cluster.py) al mismo valor 10/20/30.

Aplicar el fichero de configuración del clúster con autoscaler [ray-cluster-autoscaler.yaml](..%2Fconfig%2Fcluster_config%2Fray-cluster-autoscaler.yaml):
```
kubectl apply -f ray-cluster.autoscaler.yaml
```
Ejecutar el port forwarding:
```
kubectl port-forward --address 0.0.0.0 svc/raycluster-autoscaler-head-svc 8265:8265
```

Ejecutar el código [1-exp3_ray_embl_inference_cluster.py](experiment_3%2F1-exp3_ray_embl_inference_cluster.py) con Ray Job:
```
ray job submit --address http://localhost:8265 --working-dir . -- python  1-exp3_ray_embl_inference_cluster.py
```
Una vez se ha redimensionado el clúster ejecutar [save_pods_times.py](experiment_3%2Fsave_pods_times.py).