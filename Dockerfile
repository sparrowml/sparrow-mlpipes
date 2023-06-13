FROM nvcr.io/nvidia/deepstream:6.2-devel

ARG USER=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-key adv --fetch-keys https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

RUN apt update -y && apt install -y sudo
RUN groupadd --gid $USER_GID $USER && \
    useradd --uid $USER_UID --gid $USER_GID -m $USER && \
    echo ${USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER} && \
    chmod 0440 /etc/sudoers.d/${USER} && \
    chsh ${USER} -s /bin/bash

RUN mkdir -p /commandhistory
RUN chown -R ${USER} /commandhistory

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" && \
  echo $SNIPPET >> "/home/${USER}/.bashrc"

RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y tzdata
RUN apt install -y \
    build-essential \
    curl \
    git

# GPU Setup
RUN apt-get install -y \
    libcairo2-dev \
    libgl1-mesa-glx \
    software-properties-common

RUN bash /opt/nvidia/deepstream/deepstream/user_deepstream_python_apps_install.sh --version 1.1.6

# GPU Setup
RUN apt-get install -y \
    libcairo2-dev \
    libgl1-mesa-glx \
    software-properties-common

# Link Python 3.8
RUN ln -s /usr/bin/python3.8 /usr/local/bin/python
RUN rm /usr/local/bin/pip
RUN ln -s /usr/local/bin/pip3.8 /usr/local/bin/pip
RUN pip install --upgrade pip

RUN mkdir -p /code
RUN chown -R ${USER} /code
WORKDIR /code

USER ${USER}
ENV PATH "${PATH}:/home/${USER}/.local/bin"

RUN mkdir sparrow_mlpipes && \
  touch sparrow_mlpipes/__init__.py
COPY setup.cfg .
COPY setup.py .
RUN pip install -U pip
RUN pip install -e .
ADD . .

ENTRYPOINT [ "make" ]