#!/bin/sh

if [ ! -d "/var/tmp/Felucca" ]; then
    git clone -b deployment https://github.com/MITS-Felucca/Felucca.git /var/tmp/Felucca
else
    git -C /var/tmp/Felucca pull
fi


