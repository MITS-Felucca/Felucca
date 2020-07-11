#!/bin/sh

if [ ! -d "/var/lib/Felucca" ]; then
    git clone https://github.com/MITS-Felucca/Felucca.git /var/lib
else
    git pull -C /var/lib/Felucca
fi


