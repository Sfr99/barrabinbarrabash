# barrabinbarrabash

## Descripción del reto

Hemos propuesto un acercamiento para proteger servidores de videojuegos con
protocolos inseguros enfocado a administradores de sistemas de servidores de
juegos autogestionados. Las imágenes para los servidores de videojuegos suelen
ser propietarias y dificultan la seguridad a nivel de aplicación. Por lo tanto,
existen muchos servidores con imagenes servidores de videojuegos con protocolos
inseguros y vulnerables a ataques DDoS, floods de conexiones, escaneos de
puertos, payloads sospechosos, etc.

Para solucionarlo hemos implementado una capa intermedia a nivel L4 que sirve
de cortafuegos dedicado a servidores de videojuegos. Para comprobar la
correcta ejecución de esta idea hemos implementado un MVP que protege a un
servidor de [Project Zomboid preexistente que autogestionamos en nuestro tiempo
libre, basado en NixOS](gitlab.com/albfsg/nixkiwi). El MVP implementa la capa
protegiendo de ataques DDoS, baneando @IPs malignas. Además expone via HTTP un
panel de administración del sistema que permite ver que ataques DDoS han
sucedido, que @IPs han sido baneadas en consecuencia y permite desbanear.

## Enfoque de la solución / Cómo funciona

Un servidor autogestionado de videojuegos puede estar montado de diversas
maneras. En nuestro caso nuestro servidor tenía abierto en un router los puertos
necesarios para jugar a Project Zomboid y los port-forwardea al servidor NixOS
que ejecuta el videojuego en un contenedor Docker. Tras implantar nuestra
solución el router port-forwardea en su lugar los paquetes UDP/TCP al proxy,
implementado en Python, que se ejecuta en segundo plano en el servidor NixOS,
el cual realiza un saneamiento de las entradas, banea @IPs si es necesario,
comunica la existencia de ataques a la aplicación web implementada en Flask y
FastAPI si es necesario y forwardea los paquetes al Docker si pasan el control.

API del backend:


- GET /state Devuelve un objeto con: attacks_today (nº ataques), banned_ips
(lista de IPs baneadas), events (lista de eventos), chart (labels/values para
gráfico)

- POST /reset Borra todos los bans y eventos

- POST /ban?ip=...&reason=... Añade una IP a la colección de baneadas

- POST /unban/{ip} Elimina la IP de la tabla de IPs baneadas

- GET /event?ip=...&action=...&description=...&is_attack=true|false Registra un
evento

- GET /chart Devuelve los datos necesarios para construir gráfico

## Cómo ejecutar o probar

### Ejecución proxy

Para ejecutar el proxy, en el servidor a defender, en el directorio
`/<WORK_DIR>/barrabinbarrabash/proxy/`:

```bash
nix-shell
python3 ./proxy.py &
```

Abrir UI desde el navegador `http://<IP_DEL_SERVIDOR>:8001/`:

### Ejecución interfaz web

#### Recomendado

```bash
cd ui/
python3 -m venv venv
pip3 install -r requirements.txt
```
Dentro de `ui/backend/`

```bash
uvicorn main:app --reload --port 5000
```
Dentro de `ui/frontend/`

```bash
python3 app.py
```

#### Alternativamente usar script

Dentro de `ui/`

```bash
chmod +x run.sh
./run.sh
```
