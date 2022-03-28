FROM python:3.6-alpine
MAINTAINER Pratik

ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers \
    && apk add libffi-dev


RUN mkdir /django_cicd
WORKDIR /django_cicd
COPY . /django_cicd/


RUN pip install --upgrade pip && pip install -r requirements.txt

RUN adduser -D user
USER user

