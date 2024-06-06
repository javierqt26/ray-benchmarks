# Ray Benchmarks

## Introducción
Este proyecto contiende código que utiliza Ray Data para la inferencia por lotes fuera de linea (Offline Batch Inference).
El código se ha desarrollado utilizando el IDE PyCharm.


## Estructura del proyecto
embl -> contiene el modelo para detectar si una imagen esta fuera de muestra. Las imágenes se pueden conseguir en MetaSpace. 

imagenet -> contiene un script para descargar imágenes del repositorio ImageNet para utilizar con [1-ray_preprocess.py](ray_local%2Fcode%2F1-ray_preprocess.py) y 
[2-ray_inference.py](ray_local%2Fcode%2F2-ray_inference.py).

plots -> contiene los resultados de las ejecuciones y los notebooks con graficas.

ray_cluster -> contiene el código preparado para la ejecución en un clúster y la guía de instalación.

ray_local -> contiene el código preparado para la ejecución en local.

## Entorno de desarollo y ejecución

Para desarrollar y ejecutar el proyecto se recomienda crear un nuevo entorno de miniconda, ya que se deben instalar versiones concretas de los paquetes.

### Instalar miniconda
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```

### Crear entorno e instalar requisitos
```
~/miniconda3/bin/conda init bash
conda create -n python311 python=3.11
conda activate python311
pip install -r requirements.txt
```

### Ejecutar código [ray_local](ray_local)
El código de Ray local, una vez creado el entorno e instalados los requisitos se puede ejecutar con el botón de Run del IDE PyCharm.

### Ejecutar código [ray_cluster](ray_cluster)
El código de Ray clúster contiene sus propias instrucciones en el directorio utilizando Ray Job.
