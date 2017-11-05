FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential


# Bundle app source
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV FLASK_APP = atlasTest.py

EXPOSE  5000
CMD ["python", "./atlasTest.py", "-p 5000"]
