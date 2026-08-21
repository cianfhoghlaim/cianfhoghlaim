# Dockerfile used to deploy the Evidence dashboard as a Huggingface Space data application
FROM ubuntu:22.04

# Install Node.js 20 - https://github.com/nodesource/distributions?tab=readme-ov-file#installation-instructions-deb
# And python3
RUN apt update \
    && apt install -y curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh \
    && bash nodesource_setup.sh \
    && apt update \
    && apt install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && rm nodesource_setup.sh

RUN pip install --upgrade "huggingface_hub[cli]"

# Build the app
WORKDIR /usr/app
COPY ./ /usr/app

## Download data files to replace to Git LTS pointer file
#RUN curl -L https://huggingface.co/spaces/foghlaimeoir/evidence_code/resolve/main/sources/pypi_analytics/pypi_analytics.duckdb -o pypi_analytics.duckdb \
#    && mv pypi_analytics.duckdb ./sources/pypi_analytics/pypi_analytics.duckdb

RUN npm install 
RUN npm run sources && npm run build


# Upload the app

## The site space name must be passed as an environment variable
## https://huggingface.co/docs/hub/spaces-sdks-docker#buildtime
ARG STATIC_SPACE
## The Hugging Face token must be passed as a secret (https://huggingface.co/docs/hub/spaces-sdks-docker#buildtime)
## 1. get README.md from the site space
RUN --mount=type=secret,id=HF_TOKEN,mode=0444,required=true \
    huggingface-cli download --token=$(cat /run/secrets/HF_TOKEN) --repo-type=space --local-dir=/usr/app/build $STATIC_SPACE README.md && rm -rf /usr/app/build/.cache
## 2. upload the new build to the site space, including README.md
RUN --mount=type=secret,id=HF_TOKEN,mode=0444,required=true \
    huggingface-cli upload --token=$(cat /run/secrets/HF_TOKEN) --repo-type=space $STATIC_SPACE /usr/app/build . --delete "*"

## Halt execution because the code space is not meant to run.
CMD ["true"]