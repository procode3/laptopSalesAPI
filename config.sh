#!/bin/bash

#BD environment variables from a .env file

#Install nmap using apt
sudo apt-get install nmap

#Start the HTTP server

ncat -lk -p 3000 --sh-exec 'echo -ne "HTTP/1.1 200 OK\r\n\r\nContent-Type: application/json\r\n\r\n{\"message\": \"Hello from LaptopSales Bash low level REST API\"}"'

