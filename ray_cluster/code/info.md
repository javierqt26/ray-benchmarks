
## Comando para ejecutar [1-ray_preprocess_cluster.py](1-ray_preprocess_cluster.py)
```
ray job submit --address http://localhost:8265 --working-dir . -- python  1-ray_preprocess_cluster.py
```

## Comando para ejecutar [2-ray_inference_cluster.py](2-ray_inference_cluster.py)
```
ray job submit --address http://localhost:8265 --working-dir . -- python  2-ray_inference_cluster.py
```

## Comando para ejecutar [3-ray_embl_preprocess_cluster.py](3-ray_embl_preprocess_cluster.py)
```
ray job submit --address http://localhost:8265 --working-dir . -- python  3-ray_embl_preprocess_cluster.py
```

## Comando para ejecutar [4-ray_embl_inference_cluster.py](4-ray_embl_inference_cluster.py)
```
ray job submit --address http://localhost:8265 --working-dir . -- python  4-ray_embl_inference_cluster.py
```