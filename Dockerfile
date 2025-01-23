FROM nvcr.io/nvidia/deepstream:7.1-triton-multiarch

ARG USER=dev
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN apt update -y && apt install -y sudo
RUN groupadd --gid $USER_GID $USER && \
    useradd --uid $USER_UID --gid $USER_GID -m $USER && \
    echo ${USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER} && \
    chmod 0440 /etc/sudoers.d/${USER} && \
    chsh ${USER} -s /bin/bash

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo $SNIPPET >> "/root/.bashrc"

# RUN apt-key adv --fetch-keys https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

# RUN apt-get update -y
# RUN apt install -y \
#     python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
#     python3 python3-pip python3.8-dev python3.8-venv cmake g++ build-essential \
#     libglib2.0-dev libglib2.0-dev-bin python-gi-dev libtool m4 autoconf automake \
#     openssh-client musl-dev libffi-dev

# RUN git config --global http.sslverify false

# WORKDIR /opt/nvidia/deepstream/deepstream
# RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git
# RUN cd deepstream_python_apps && \
#     git checkout 0148b5afc4e1c3f1c640cb06cac6e2bc050cacff && \
#     git submodule update --init && \
#     cd 3rdparty/gst-python && \
#     ./autogen.sh && \
#     make && \
#     make install
# RUN cd deepstream_python_apps/bindings && \
#     mkdir build && \
#     cd build && \
#     cmake .. -DPYTHON_MAJOR_VERSION=3 -DPYTHON_MINOR_VERSION=8 && \
#     make && \
#     pip3 install pyds-*.whl

RUN ln -s /usr/bin/python /usr/local/bin/python
RUN pip install -U pip

RUN mkdir -p /code
RUN chown -R ${USER} /code
WORKDIR /code

USER ${USER}
ENV PATH "${PATH}:/home/${USER}/.local/bin"

RUN mkdir sparrow_mlpipes && \
  touch sparrow_mlpipes/__init__.py
COPY setup.cfg .
COPY setup.py .
COPY requirements.txt .
RUN pip install -U pip
RUN pip install -r requirements.txt

ADD . .

