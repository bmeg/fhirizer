FROM python:3.13

RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app
COPY . /app

RUN pip install -e .

ENV PYTHONPATH=/app

ENTRYPOINT ["/bin/bash"]