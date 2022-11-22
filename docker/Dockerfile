FROM python:3.9-slim-bullseye

RUN apt-get update -y
RUN apt-get install gcc -y

WORKDIR /usr/src/regnify-api
RUN mkdir /usr/src/regnify-api/requirements

COPY requirements/* /usr/src/regnify-api/requirements

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /usr/src/regnify-api/requirements/prod.txt

ADD .. /usr/src/regnify-api/
WORKDIR /usr/src/regnify-api/
EXPOSE 8100

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:8100", "-t 30" , "-k", "uvicorn.workers.UvicornWorker", "src.main:app" ]