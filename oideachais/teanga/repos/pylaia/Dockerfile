FROM nvidia/cuda:12.3.2-base-ubuntu22.04

# Add python3 in cuda image
ENV DEBIAN_FRONTEND=non-interactive
RUN apt-get update -q -y && apt-get install -q -y --no-install-recommends python3-pip git

# Update pip setuptools
RUN pip install -U pip setuptools

# Setup pylaia library
WORKDIR /src
COPY laia /src/laia
COPY LICENSE pyproject.toml MANIFEST.in README.md /src

RUN pip install . --no-cache-dir
