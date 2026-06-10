#!/bin/bash

set -eux 

./gradlew clean
find . -name .cxx -a -type d | xargs rm -rf
find . -name build -a -type d | xargs rm -rf
find . -name .gradle -a -type d | xargs rm -rf
find . -name .idea -a -type d | xargs rm -rf
