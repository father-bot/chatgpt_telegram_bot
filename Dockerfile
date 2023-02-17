FROM python:3.8-alpine AS builder

RUN apk update && apk add gcc musl-dev && pip install pdm

COPY . /code

RUN cd /code && pdm install --prod --no-lock --no-editable

FROM python:3.8-alpine

COPY --from=builder /code /code

WORKDIR /code

CMD [ "/code/.venv/bin/python", "/code/bot/bot.py" ]