FROM python:3.9-alpine

COPY . /app
WORKDIR /app

RUN apk add --no-cache bash ffmpeg

RUN pip install -r requirements.txt

CMD ["/bin/bash", "run.sh"]