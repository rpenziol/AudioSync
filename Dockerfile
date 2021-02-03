FROM python:3.6

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get -y install ffmpeg

RUN pip install -r requirements.txt

CMD ["/bin/bash", "run.sh"]