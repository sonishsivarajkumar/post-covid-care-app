FROM node:10.15.0 as client-app

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev python3-pip

WORKDIR /app
COPY . .

RUN chmod +x /app/start.sh
#RUN chmod 600 /app/src/aiml_post_covid_care/utils/database_connect/certificates/*

RUN pip3 install -r requirements.txt


EXPOSE 3015

CMD ["./start.sh"]
