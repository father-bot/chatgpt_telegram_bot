FROM python:3.8-alpine

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apk add --no-cache python3-dev build-base libffi-dev openssl-dev ffmpeg
RUN apk add --no-cache bash

RUN mkdir -p /code
ADD . /code
WORKDIR /code

RUN pip3 install -r requirements.txt

CMD ["bash"]
