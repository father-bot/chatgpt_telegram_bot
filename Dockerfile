FROM python:3.8-slim as dependencies

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && \
    apt-get install -y build-essential


COPY requirements.txt /
WORKDIR /dependencies

RUN pip3 install --target=/dependencies -r /requirements.txt


FROM python:3.8-slim as final

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONPATH="${PYTHONPATH}:/dependencies"

WORKDIR /app

COPY --from=dependencies /dependencies /dependencies
COPY . .

ENTRYPOINT ["python3", "bot/bot.py"]
