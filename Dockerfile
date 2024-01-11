FROM python:3.8-slim


RUN set -eux;
RUN apt-get update;
RUN apt-get install -y --no-install-recommends \
    python3-pip \
    build-essential \
    python3-venv \
    ffmpeg \
    git
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip && pip3 install -U wheel && pip3 install -U setuptools==59.5.0
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && rm -r /tmp/requirements.txt

COPY . /code
WORKDIR /code

CMD ["bash"]

