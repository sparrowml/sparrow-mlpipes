FROM nvcr.io/nvidia/deepstream:6.2-devel

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

RUN ln -s /usr/bin/python3 /usr/local/bin/python
RUN pip install -U pip

RUN sudo bash /opt/nvidia/deepstream/deepstream/user_additional_install.sh
RUN sudo bash /opt/nvidia/deepstream/deepstream/user_deepstream_python_apps_install.sh --version 1.1.6

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
