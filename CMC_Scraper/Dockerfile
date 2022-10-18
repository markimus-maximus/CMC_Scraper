FROM ubuntu:latest

RUN apt update
RUN apt install python3 -y
RUN set -xe \
    && apt-get update -y \
    && apt-get install -y python3-pip

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD ["python3", "__main__.py"]