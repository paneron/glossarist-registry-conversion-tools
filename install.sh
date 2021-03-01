#!/bin/bash

# sudo apt-get update -y

project_dir=`pwd`

python3 -m venv ${project_dir}/venv

source ${project_dir}/venv/bin/activate

${project_dir}/venv/bin/pip3 install --upgrade pip
pip install -r ${project_dir}/requirements.txt

cp ${project_dir}/config.py.sample ${project_dir}/config.py
