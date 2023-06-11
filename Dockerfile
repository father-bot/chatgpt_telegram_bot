FROM python:3.8-slim

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && \
  apt-get install -y \
    # required by the bot
    python3-yaml python3-pymongo ffmpeg \
    # debugging helpers
    nano ripgrep && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ADD . /code

CMD ["bash"]
