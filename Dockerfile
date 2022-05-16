FROM nvcr.io/nvidia/deepstream:6.0-triton

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" && echo $SNIPPET >> "/root/.bashrc"

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH="${PATH}:/root/.poetry/bin"

RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list
RUN apt-key del 7fa2af80
RUN apt-get update && apt-get install -y --no-install-recommends wget
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb
RUN dpkg -i cuda-keyring_1.0-1_all.deb

RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y tzdata
RUN apt install -y \
    build-essential \
    curl \
    git \
    libcairo2-dev \
    libgl1-mesa-glx \
    software-properties-common

# Install Python 3.9
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9-dev python3.9-venv
RUN python3.9 -m ensurepip
RUN ln -s /usr/bin/python3.9 /usr/local/bin/python
RUN ln -s /usr/local/bin/pip3.9 /usr/local/bin/pip
RUN pip install --upgrade pip

# Allow root for Jupyter notebooks
RUN mkdir /root/.jupyter
RUN echo "c.NotebookApp.allow_root = True" > /root/.jupyter/jupyter_notebook_config.py

RUN git config --global http.sslverify false

WORKDIR /opt/nvidia/deepstream/deepstream
RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git
RUN cd deepstream_python_apps && \
    git checkout 0148b5afc4e1c3f1c640cb06cac6e2bc050cacff && \
    git submodule update --init && \
    cd 3rdparty/gst-python && \
    ./autogen.sh && \
    make && \
    make install
RUN cd deepstream_python_apps/bindings && \
    mkdir build && \
    cd build && \
    cmake .. -DPYTHON_MAJOR_VERSION=3 -DPYTHON_MINOR_VERSION=9 && \
    make && \
    pip install pyds-*.whl

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=true
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

CMD mkdir -p /code
WORKDIR /code

ADD . .
ENTRYPOINT [ "make" ]
