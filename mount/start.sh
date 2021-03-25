#!/bin/bash

docker run -it --rm --name netstate -v mongodbdata:/data/db -v $(pwd):/var/www/logs -p 5000:5000 netstate:dev

