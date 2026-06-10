#!/bin/bash -x

podman compose -f ./cocoindex/dev/postgres.yaml up -d
podman logs -f cocoindex-postgres_postgres_1
