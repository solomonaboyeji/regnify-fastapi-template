FROM python:3.9-slim-bullseye

RUN apt-get update -y
RUN apt-get install gcc -y

WORKDIR /usr/src/regnify-api
RUN mkdir /usr/src/regnify-api/requirements

COPY requirements.txt /usr/src/regnify-api/requirements/prod.txt

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /usr/src/regnify-api/requirements/prod.txt

ADD .. /usr/src/regnify-api/
WORKDIR /usr/src/regnify-api/
EXPOSE 8100

CMD ["hypercorn", "src.main:app", "--workers", "1", "--bind",  "0.0.0.0:8100" ]