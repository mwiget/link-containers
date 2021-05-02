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
docker run -ti --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock --pid host marcelwiget/link-containers c1/c2
docker run -ti --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock --pid host marcelwiget/link-containers c1/c2

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

Using docker-compose, creating multiple links, optionally with large MTU:

```
  links:
    image: marcelwiget/link-containers
    privileged: true
    network_mode: none
    restart: "no"
    pid: "host"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: r1/host1 r1/host2/3000
```

# build multi-arch container

Follow the instructions on https://www.docker.com/blog/multi-arch-images/ to create mybuilder, then use
buildx:

```
docker buildx create --name mybuilder
docker buildx use mybuilder
```

Now build and push the container (change first tag to match your image repository service):

```
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t marcelwiget/link-containers --push .
```
Verify with imagetools to inspect the container image:

```
$ docker buildx imagetools inspect marcelwiget/link-containers
Name:      docker.io/marcelwiget/link-containers:latest
MediaType: application/vnd.docker.distribution.manifest.list.v2+json
Digest:    sha256:310ec786767c9423264a912e3f5b863deeb6ba5cc33d05e08d996d483863e328

Manifests:
  Name:      docker.io/marcelwiget/link-containers:latest@sha256:67264eace498b7527a91e5741dd111799aab9a0f69b751f97f4a6c7634baa17d
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/amd64

  Name:      docker.io/marcelwiget/link-containers:latest@sha256:aed73ba9f7ff8068dc9d3fce3cd0a5115f36a4d182dd059279ab5e6c80bfe82f
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/arm64

  Name:      docker.io/marcelwiget/link-containers:latest@sha256:6564e0b37412dc872e8512f94da3bda884dbb9e6fea15d48d295738b500f3725
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  linux/arm/v7
```
