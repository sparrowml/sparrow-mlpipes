FROM python:3.6

# Cuda base image
# FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo $SNIPPET >> "/root/.bashrc"

# Install Python
# RUN apt-get update -y
# RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
# RUN apt install -y \
#     build-essential \
#     git \
#     libgl1-mesa-glx \
#     software-properties-common

# RUN add-apt-repository ppa:deadsnakes/ppa
# RUN apt install -y python3.9-dev python3.9-venv
# RUN python3.9 -m ensurepip
# RUN ln -s /usr/bin/python3.9 /usr/local/bin/python
# RUN ln -s /usr/local/bin/pip3.9 /usr/local/bin/pip

RUN pip install poetry==1.1.6

RUN mkdir -p /code/mlpipes
WORKDIR /code
RUN touch mlpipes/__init__.py

COPY poetry.toml pyproject.toml /code/

# Include poetry.lock when it's available
# COPY poetry.lock poetry.toml pyproject.toml /code/

RUN poetry install
