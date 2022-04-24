#Deriving the latest base image
FROM python:latest


#Labels as key value pair
LABEL Maintainer="brantje"

WORKDIR /usr/app/src

RUN pip install -r requirements.txt

COPY main.py ./
CMD [ "python", "./main.py"]
