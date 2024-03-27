FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    python3 \
    python3-setuptools \
    python3-pip \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

COPY . /app
WORKDIR /app
RUN pip install .

ENV PYTHONPATH="$PYTHONPATH:/app"