#  Start with python base image
FROM python:3.7-slim-buster

LABEL network_state_beta="0.1"

# working directory
WORKDIR /var/www

# Copy over requirements file
COPY requirements.txt /tmp/

#install GIT
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git


# Run pip
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt


#create
RUN mkdir -p /data

# mount volume
VOLUME  /data/db

# Update apt-get sources AND install MongoDB
# Import MongoDB public GPG key AND create a MongoDB list file
# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install necessary libs
RUN apt-get install -y apt-utils wget gnupg gnupg2 curl

# Install mongodb
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
RUN echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list
RUN apt-get update
RUN apt-get install -y mongodb-org && apt-get install -y telnet && rm -rf /var/lib/apt/lists/*

# BIND TO ALL ADAPTERS IN CONTAINER
RUN sed -i "s,\\(^[[:blank:]]*bindIp:\\) .*,\\1 0.0.0.0," /etc/mongod.conf

#Telnet
#RUN apt-get install telnet

#Flask Port
EXPOSE 5000

# copy ./source_files subdirectory to working directory within container
COPY ./source_files .

#make start python file executeable
RUN chmod +x wsgi.py
RUN chmod +x action.sh

#Script for:
#Use Gunicorn as WSGI for app
#MongoDB start script
#Mongodb import
CMD ["/var/www/action.sh"]
