#!/bin/bash

solution_dir="/home/HwHiAiUser/eias/"
echo "solution_dir is ${solution_dir}"

echo "boot robot client"
java -jar ./robot-client-1.0.jar > ${solution_dir}/log/robot-client.log &
sleep 3
echo "boot eagle"
sudo chmod 777 /dev/tty*
python ${solution_dir}/eagle/main.py ${solution_dir}/log/eagle.log > ${solution_dir}/log/gomi.log &
