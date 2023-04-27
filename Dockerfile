FROM python:3.9.16-alpine

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apk update && apk add --no-cache ffmpeg

RUN mkdir -p /code
WORKDIR /code
ADD requirements.txt .

RUN pip3 install -r requirements.txt

ADD . .

CMD ["python3", "bot/bot.py"]
