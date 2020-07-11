#!/bin/sh

if [ ! -d "/var/tmp/Felucca" ]; then
    git clone https://github.com/MITS-Felucca/Felucca.git /var/tmp/Felucca
else
    git -C /var/tmp/Felucca pull
fi


