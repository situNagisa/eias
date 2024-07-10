#!/bin/bash

solution_dir=/home/HwHiAiUser/eias

cd ${solution_dir}
./scripts/build_python.sh
./scripts/build_java.sh
./scripts/build_acllite.sh
./scripts/build_camera.sh
