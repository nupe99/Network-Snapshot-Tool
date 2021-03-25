#!/bin/bash

#Create SSC
openssl genrsa -des3 -passout pass:pass123 -out server.pass.key 2048
openssl rsa -passin pass:pass123 -in server.pass.key -out server.key
rm server.pass.key
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=NJ/L=Trenton/O=Mine/OU=IT Department/CN=lab.com"
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

#Start MongoDB
/usr/bin/mongod --fork --logpath=/var/log/mongod.log

#Import empty DB structure
/usr/bin/mongorestore --archive=/var/www/network_state.001.archive

#Start Gunicorn
#gunicorn -w 4 --bind 0.0.0.0:5000 --chdir /var/www wsgi:app
gunicorn --certfile server.crt --keyfile server.key -w 4 --bind 0.0.0.0:5000 --chdir /var/www wsgi:app
