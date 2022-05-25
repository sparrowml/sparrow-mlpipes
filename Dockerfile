FROM nvcr.io/nvidia/deepstream:6.0-triton

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && echo $SNIPPET >> "/root/.bashrc"

RUN apt-key adv --fetch-keys https://developer.download.nvidia.cn/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

RUN apt-get update -y
RUN apt install -y \
    python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
    python3 python3-pip python3.8-dev python3.8-venv cmake g++ build-essential \
    libglib2.0-dev libglib2.0-dev-bin python-gi-dev libtool m4 autoconf automake \
    openssh-client

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
    cmake .. -DPYTHON_MAJOR_VERSION=3 -DPYTHON_MINOR_VERSION=8 && \
    make && \
    pip3 install pyds-*.whl

RUN rm /usr/bin/python /usr/local/bin/pip
RUN ln -s /usr/bin/python3.8 /usr/local/bin/python
RUN ln -s /usr/local/bin/pip3.8 /usr/local/bin/pip

# Allow root for Jupyter notebooks
RUN mkdir /root/.jupyter
RUN echo "c.NotebookApp.allow_root = True" > /root/.jupyter/jupyter_notebook_config.py

# Install Poetry
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
