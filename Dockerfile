FROM python:3.11-slim AS build-env

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN apt update && apt install --no-install-recommends -y python3 python3-pip python-dev-is-python3 build-essential python3-venv ffmpeg && \
    python -m venv /opt/venv 
ENV PATH="/opt/venv/bin:$PATH"
ADD ./bot /app
WORKDIR /app
RUN /opt/venv/bin/pip3 --no-cache-dir install -r requirements.txt 

FROM python:3.11-slim
RUN apt update && apt install ffmpeg
COPY --from=build-env /opt/venv /opt/venv
COPY --from=build-env /app /app
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["/opt/venv/bin/python3", "/app/bot.py"]
