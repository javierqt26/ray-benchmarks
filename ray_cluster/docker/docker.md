# Imagen Docker
## 1. Crear Dockerfile

Es necesario crear un Dockerfile, para este proyecto se ha creado el siguiente [Dockerfile](Dockerfile) que hace uso de la imagen base de Ray 2.9.3 con Python 3.11 y añade las dependencias necesarias (los paquetes y el modelo) para la ejecución del código desarrollado.

## 2. Construir imagen
Para construir la imagen es necesario ubicar temporalmente el modelo [torchscript_model_2.1.2.pt](..%2F..%2Fembl%2Ftorchscript_model_2.1.2.pt) en este directorio y ejecutar el siguiente comando:
```
docker build -t javierqt26/ray_py311_requirements .
```

## 3. Publicar imagen
Con el siguiente comando se puede publicar la imagen en Docker Hub:
```
docker push javierqt26/ray_py311_requirements
```



