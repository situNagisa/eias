#!/bin/bash

solution_dir=/home/HwHiAiUser/eias/

cd ${solution_dir}

git clone https://gitee.com/ascend/ACLLite.git

export DDK_PATH=/usr/local/Ascend/ascend-toolkit/latest
export NPU_HOST_LIB=$DDK_PATH/runtime/lib64/stub

chmod +x ./ACLLite/build_so.sh
./ACLLite/build_so.sh


cd -
