FROM alpine:edge

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apk add --no-cache python3 py3-pip openssl
RUN apk add --no-cache ffmpeg
WORKDIR /
ADD . /
COPY config/api.example.yml /config/api.yml
COPY config/chat_mode.example.yml /config/chat_mode.yml
COPY config/model.example.yml /config/model.yml
RUN pip3 install -r requirements.txt
CMD ["python3", "/bot/bot.py"]
