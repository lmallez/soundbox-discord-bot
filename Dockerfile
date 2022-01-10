FROM python:3.8

USER root
WORKDIR /home/soundbox
COPY requirements.txt ./

RUN apt-get -y update
RUN apt-get install -y ffmpeg

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "./main.py"]
