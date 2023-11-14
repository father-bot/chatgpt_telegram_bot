FROM python:3.8-slim-bookworm

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip3 install -U pip && pip3 install -U wheel && pip3 install -U setuptools==59.5.0
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && rm -r /tmp/requirements.txt

COPY . /code
WORKDIR /code

CMD ["bash"]

