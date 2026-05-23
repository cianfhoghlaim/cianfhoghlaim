#!/bin/bash

if command -v docker &> /dev/null
then
	CONTAINER_RUNTIME=docker
elif command -v podman &> /dev/null
then
	CONTAINER_RUNTIME=podman
else
	echo "Failed to find docker or podman"
	exit 1
fi

$CONTAINER_RUNTIME run --rm -it -v $(pwd):/build/docs.beagleboard.org:rw,z -p 8000:8000 beagle/sphinx-build-env /bin/bash
