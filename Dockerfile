FROM python:3.12-slim

# flush stdout/stderr immediately so logs show up in `docker logs`
ENV PYTHONUNBUFFERED=1

RUN \
    set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
    python3-pip \
    build-essential \
    python3-venv \
    ffmpeg \
    git \
    ; \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -U pip && pip3 install --no-cache-dir -U wheel && pip3 install --no-cache-dir -U setuptools
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm -r /tmp/requirements.txt

COPY . /code
WORKDIR /code

CMD ["bash"]

