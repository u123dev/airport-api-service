FROM python:3.12-alpine
LABEL maintainer="u123@ua.fm"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt ./
RUN pip install -r  requirements.txt
COPY . .

RUN mkdir -p /media

RUN adduser \
    --disabled-password\
    --no-create-home\
    airport-user

RUN chown -R airport-user /media/
RUN chmod -R 755 /media

USER airport-user
