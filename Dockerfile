FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update

RUN apt-get install -y python3

RUN apt -y install python3-pip

COPY . .

RUN apt install -y libmysqlclient-dev

RUN pip install -r requirements.txt 

EXPOSE 8080:8080

CMD [ "python3", "app.py" ]