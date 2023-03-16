FROM python:3.8-alpine

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apk --no-cache add ffmpeg

WORKDIR /code

COPY requirements.txt /code/

RUN pip3 install -r requirements.txt

ADD . /code

CMD ["python3", "/code/bot/bot.py"]
