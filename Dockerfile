# syntax=docker/dockerfile:labs

FROM python:3.8-slim as builder
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update
RUN apt-get install -y --no-install-recommends python3 python3-pip python3-dev build-essential python3-venv

WORKDIR /build
ADD requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip3 wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.8-slim
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
ADD requirements.txt requirements.txt
RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels pip3 install --upgrade --no-index --find-links=/wheels -r requirements.txt

ADD . /app

CMD /usr/local/bin/python /app/bot/bot.py