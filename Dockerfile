FROM python:3

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install ffmpeg

RUN pip install pipenv
RUN pipenv install --system --deploy

CMD ["/bin/bash", "run.sh"]