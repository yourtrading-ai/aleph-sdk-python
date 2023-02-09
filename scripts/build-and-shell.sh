#!/bin/sh

set -euf

# Use Podman if installed, else use Docker
if hash podman 2> /dev/null
then
  DOCKER_COMMAND=podman
else
  DOCKER_COMMAND=docker
fi

$DOCKER_COMMAND build -t aleph-sdk-python -f docker/Dockerfile .
$DOCKER_COMMAND run -ti --rm --entrypoint /bin/bash -v "$(pwd)":/opt/aleph-sdk-python aleph-sdk-python
