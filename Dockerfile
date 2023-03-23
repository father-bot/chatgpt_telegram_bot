FROM python:3.8-slim

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python-dev \
    build-essential \
    python3-venv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code/bot /code/config
ADD . /code
WORKDIR /code

RUN pip3 install --no-cache-dir -r requirements.txt

VOLUME ./bot:/code/bot
VOLUME ./config:/code/config

CMD ["bash"]
