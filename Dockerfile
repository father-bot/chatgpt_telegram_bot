FROM python:3.9.16-alpine

RUN apk update && apk add --no-cache ffmpeg
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && rm -r /tmp/requirements.txt

RUN mkdir -p /code
COPY . /code
WORKDIR /code

CMD ["python3", "bot/bot.py"]
