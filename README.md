# link-containers

This helper container creates a veth link and places the endpoints into both containers provided as arguments and renames them,
so that they use the next available eth# name. The container terminates after completion. Clean up of the veth link happens
automatically when either container terminates.

Example:

```
$ cat link-alpine.sh
#!/bin/sh
docker stop c1 c2 || true

docker run -ti -d --rm --name c1 --cap-add NET_ADMIN alpine
docker run -ti -d --rm --name c2 --cap-add NET_ADMIN alpine

echo "connect $1 with $2 with 2 links ..."
docker run -ti --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock --pid host marcelwiget/link-containers c1 c2
docker run -ti --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock --pid host marcelwiget/link-containers c1 c2

docker ps

echo "show interfaces in container c1:"
docker exec -ti c1 ip link
```

```
$ ./link-alpine.sh 
f8f8f0b8b03c5765dddbda62bed4f4bb1c0508fd4c0d9bd078d2ebced179050f
82da9227ea1029bb98b3a20fedef8ba5278c2b640466cb65a43e604e65d3158a
connect  with  with 2 links ...
Unable to find image 'marcelwiget/link-containers:latest' locally
latest: Pulling from marcelwiget/link-containers
596ba82af5aa: Already exists 
4fb82344e93c: Pull complete 
9798e75c1fc8: Pull complete 
1cc591c5c392: Pull complete 
Digest: sha256:4d581bb43e98c43bc5d9e9d6002830dff582d6be669308009007d765b4777f03
Status: Downloaded newer image for marcelwiget/link-containers:latest
link c1:eth1 <---> c2:eth1 created
link c1:eth2 <---> c2:eth2 created
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
82da9227ea10        alpine              "/bin/sh"           7 seconds ago       Up 6 seconds                            c2
f8f8f0b8b03c        alpine              "/bin/sh"           7 seconds ago       Up 6 seconds                            c1
show interfaces in container c1:
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth2@eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP qlen 1000
    link/ether ae:a7:eb:7b:d3:86 brd ff:ff:ff:ff:ff:ff
3: eth1@eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP qlen 1000
    link/ether 3a:ad:fe:f9:f8:02 brd ff:ff:ff:ff:ff:ff
135: eth0@if136: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP 
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff
```
