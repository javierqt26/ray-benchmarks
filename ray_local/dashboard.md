# Configuración Ray Dashboard 
Ray tiene la opción de visualizar diversas estadísticas desde Ray Dashboard. Para configurar-lo sigue los siguientes pasos. 
 
## Requisitos 
### 1. Ray default 
Para instalar Ray Dashboard se requiere el package ray[default], se puede instalar con el siguiente comando (Se recomienda la versión 2.9.3) 
``` 
pip install ray[default]==2.9.3 
``` 
 
### 2. Prometheus y Grafana 
Adicionalmente se puede instalar Prometheus y Grafana para mostrar gráficos de las estadísticas. 
 
#### 2.1 Para instalar Prometheus se deben ejecutar los siguientes comandos. (Se recomienda la versión 2.45.3) 
``` 
wget https://github.com/prometheus/prometheus/releases/download/v2.45.3/prometheus-2.45.3.linux-amd64.tar.gz 
tar xvfz prometheus-*.tar.gz 
``` 
#### 2.2 Para instalar Grafana se deben ejecutar los siguientes comandos. (Se recomienda la versión 7.15.5) 
Es importante que se instale una versión anterior a la 9.x.x, ya que actualmente, Ray depende del soporte de Angular por parte de Grafana y ha sido deprecado en la versión 9. 
``` 
sudo apt-get install -y adduser libfontconfig1 musl 
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_7.5.15_amd64.deb 
sudo dpkg -i grafana-enterprise_7.5.15_amd64.deb 
``` 
 
## Ejecución 
Para ejecutar Ray Dashboard se debe de seguir el siguiente orden: 
### 1. Iniciar Ray 
``` 
ray start --head 
``` 
### 2. Iniciar Prometheus 
Una vez ejecutado Ray se debe iniciar Prometheus con el fichero de configuración que proporciona Ray. 
``` 
cd prometheus-* 
./prometheus --config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml 
``` 
 
### 3. Iniciar Grafana 
Antes de ejecutar Grafana se debe de modificar también su fichero de configuración ubicado en `/etc/grafana/grafana.ini`, remplazando el contenido por el del fichero de configuración que proporciona Ray en `/tmp/ray/session_latest/metrics/grafana/grafana.ini`. Este paso solo se debe realizar la primera vez. 
El contenido de este fichero es el siguiente. 
``` 
[security] 
allow_embedding = true 
 
[auth.anonymous] 
enabled = true 
org_name = Main Org. 
org_role = Viewer 
 
[paths] 
provisioning = /tmp/ray/session_latest/metrics/grafana/provisioning 
``` 
Grafana se ejecuta como un servicio de systemd. Para iniciar-lo y comprobar que se esta ejecutando correctamente se deben ejecutar los siguientes comandos. 
``` 
ray start --head 
sudo systemctl start grafana-server 
sudo systemctl status grafana-server 
``` 
 
## Visualizar información 
Si la configuración predeterminada no se ha modificado se pueden acceder a los dashboards des de los siguientes enlaces. 
#### Ray Dashboard http://localhost:8265/ 
#### Prometheus http://localhost:9090/ 
#### Grafana http://localhost:3000/ 



 