SHELL := /bin/bash

# all monitor components share/use the following targets/exports
DOCKER_HOST = $(shell echo $$DOCKER_HOST)
BUILD_TAG ?= git-$(shell git rev-parse --short HEAD)
DRYCC_REGISTRY ?= ${DEV_REGISTRY}
IMAGE_PREFIX ?= drycc

include includes.mk
include versioning.mk
include deploy.mk

TEST_ENV_PREFIX := docker run --rm -v ${CURDIR}:/bash -w /bash drycc/go-dev

build: docker-build
push: docker-push
deploy: check-kubectl docker-build docker-push install

docker-build:
	docker build ${DOCKER_BUILD_FLAGS} -t ${IMAGE} rootfs
	docker tag ${IMAGE} ${MUTABLE_IMAGE}

clean: check-docker
	docker rmi $(IMAGE)
	
test: test-style

test-style:
	${TEST_ENV_PREFIX} shellcheck $(SHELL_SCRIPTS)

.PHONY: build push docker-build clean upgrade deploy test test-style

build-all:
	docker build ${DOCKER_BUILD_FLAGS} -t ${DRYCC_REGISTRY}${IMAGE_PREFIX}/influxdb:${VERSION} influxdb/rootfs

push-all:
	docker push ${DRYCC_REGISTRY}${IMAGE_PREFIX}/influxdb:${VERSION}
