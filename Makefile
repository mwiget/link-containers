all: build run

build:
	docker build -t link-containers .

buildx:
	docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t marcelwiget/link-containers --push .

run:
	docker run -ti --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock --pid host --entrypoint /bin/ash link-containers
