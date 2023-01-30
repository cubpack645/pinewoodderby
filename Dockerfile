FROM python:3.10-bullseye

RUN apt-get update && apt-get install -yqq tzdata

ENV TZ="America/Los_Angeles"

COPY requirements.txt /app/

RUN pip install --upgrade pip \
	&& pip install -r /app/requirements.txt

COPY .env /app/
COPY derby /app/derby
COPY bin/pack /app/

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"
