FROM ubuntu:22.04 AS app

ENV PYTHONPATH /srv/app

WORKDIR /srv/app

# System dependencies (Cached layer)
RUN apt update -y && \
    apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update -y && \
    apt upgrade -y && \
    apt install -y \
        python3-pip \
        ffmpeg \
        libsm6 \
        libxext6 \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        '^libxcb.*-dev' \
        libx11-xcb-dev \
        libglu1-mesa-dev \
        libxrender-dev \
        libxi-dev \
        libxkbcommon-dev \
        libxkbcommon-x11-dev \
        libegl1

# Python dependencies (Cached layer)
COPY requirements.txt /srv/app/requirements.txt
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    pip3 install tesserocr

# Application code (Changed frequently)
COPY . /srv/app

WORKDIR /srv/app/poker