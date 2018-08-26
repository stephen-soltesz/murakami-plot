# FROM alpine:3.8
FROM arm32v6/alpine

ADD repositories /etc/apk/

RUN apk add --update libstdc++ python py-pip
RUN apk add libressl libevent ca-certificates
RUN update-ca-certificates

RUN pip install --upgrade pip
RUN pip install pytz tzlocal flask
RUN apk add --no-cache --virtual .build-deps \
        gcc \
        build-base \
        python-dev \
        libpng-dev \
        musl-dev \
        freetype-dev

RUN pip install --prefer-binary matplotlib
RUN apk del .build-deps
RUN apk add freetype libpng

ADD scatter.py /
WORKDIR /
